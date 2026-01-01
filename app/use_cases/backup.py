
import io
import logging
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from app.infrastructure.database.db_helper import session_factory
from app.infrastructure.database.models import User, Channel, Referral, PointHistory, Reward, UserReward, UserSurveyAnswer, WebinarSettings, Admin

logger = logging.getLogger(__name__)

class BackupService:
    def __init__(self):
        pass

    async def create_backup(self) -> bytes:
        """
        Dumps all key tables to an Excel file and returns the bytes.
        """
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        
        async with session_factory() as session:
            # List of models to backup
            models = [
                (User, "users"),
                (Channel, "channels"),
                (Referral, "referrals"), 
                (PointHistory, "point_history"),
                (Reward, "rewards"),
                (UserReward, "user_rewards"),
                (UserSurveyAnswer, "user_survey_answers"),
                (WebinarSettings, "webinar_settings"),
                (Admin, "admins")
            ]
            
            for model, sheet_name in models:
                try:
                    stmt = text(f"SELECT * FROM {model.__tablename__}")
                    result = await session.execute(stmt)
                    rows = result.fetchall()
                    keys = result.keys()
                    
                    if rows:
                        df = pd.DataFrame([dict(zip(keys, row)) for row in rows])
                        
                        # Convert datetime objects to string to avoid timezone issues in Excel
                        for col in df.columns:
                            if pd.api.types.is_datetime64_any_dtype(df[col]):
                                df[col] = df[col].astype(str)
                                
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                    else:
                        # Create empty sheet with columns if no data
                        pd.DataFrame(columns=[c.name for c in model.__table__.columns]).to_excel(writer, sheet_name=sheet_name, index=False)
                        
                except Exception as e:
                    logger.error(f"Error backing up {sheet_name}: {e}")
            
        writer.close()
        output.seek(0)
        return output.getvalue()

    async def restore_backup(self, file_content: bytes):
        """
        Restores database from an Excel file.
        WARNING: This deletes all existing data!
        """
        try:
            xls = pd.ExcelFile(io.BytesIO(file_content))
        except Exception as e:
            raise ValueError(f"Invalid Excel file: {e}")
        
        # Validation: Check if critical sheets exist
        required_sheets = ["users", "channels"]
        if not all(sheet in xls.sheet_names for sheet in required_sheets):
            raise ValueError(f"Backup file is missing required sheets: {required_sheets}. Are you sure this is a Backup file?")

        async with session_factory() as session:
            try:
                # 1. Clear existing data (Order matters due to Foreign Keys!)
                # Deleting children first
                tables_to_clear = [
                    "user_rewards",
                    "referrals",
                    "point_history",
                    "user_survey_answers",
                    "users",
                    "channels", 
                    "rewards",
                    "webinar_settings",
                    "admins"
                ]
                
                for table in tables_to_clear:
                    await session.execute(text(f"DELETE FROM {table}"))
                
                # REMOVED commit here to ensure atomicity. If insert fails, delete rolls back.
                
                # 2. Import data (Order matters: Parents first)
                sheet_to_model = {
                    "users": User,
                    "channels": Channel,
                    "referrals": Referral,
                    "point_history": PointHistory,
                    "rewards": Reward,
                    "user_rewards": UserReward,
                    "user_survey_answers": UserSurveyAnswer,
                    "webinar_settings": WebinarSettings,
                    "admins": Admin
                }
                
                import_order = [
                    "admins",
                    "channels",
                    "rewards",
                    "users",
                    "referrals",
                    "point_history",
                    "user_survey_answers",
                    "user_rewards",
                    "webinar_settings"
                ]
                
                # Fields that MUST be integers
                int_fields = [
                    "id", "telegram_id", "referrer_id", "referred_id", 
                    "user_id", "reward_id", "balance", "amount", "cost"
                ]

                for sheet_name in import_order:
                    if sheet_name in xls.sheet_names and sheet_name in sheet_to_model:
                        try:
                            df = pd.read_excel(xls, sheet_name=sheet_name)
                            
                            if df.empty:
                                continue
                                
                            data = df.to_dict(orient='records')
                            
                            # Clean data: Replace NaN with None, handle timestamps, force ints
                            cleaned_data = []
                            for row in data:
                                clean_row = {}
                                for k, v in row.items():
                                    if pd.isna(v):
                                        clean_row[k] = None
                                    else:
                                        # Force integer conversion for ID-like fields
                                        if k in int_fields:
                                            try:
                                                clean_row[k] = int(float(v))
                                            except:
                                                clean_row[k] = v # Fallback if not convertible
                                        else:
                                            clean_row[k] = v
                                        
                                # Check for fields that should be datetime
                                for col in clean_row:
                                    if "created_at" in col or "updated_at" in col or "webinar_datetime" in col:
                                        val = clean_row.get(col)
                                        if val and isinstance(val, str):
                                            try:
                                                # Clean up common issues like "2023-12-25 10:00:60" or space trimming
                                                val = val.strip()
                                                clean_row[col] = datetime.fromisoformat(val)
                                            except ValueError:
                                                # If format is totally wrong or has 60 seconds, fallback to current time
                                                # This prevents "second must be in 0..59" and "invalid datetime format" errors
                                                logger.warning(f"Invalid timestamp found in {col}: {val}. Using current time.")
                                                clean_row[col] = datetime.now()
                                                
                                cleaned_data.append(clean_row)

                            if cleaned_data:
                                await session.execute(
                                    text(f"INSERT INTO {sheet_name} ({', '.join(cleaned_data[0].keys())}) VALUES ({', '.join([':' + k for k in cleaned_data[0].keys()])})"), 
                                    cleaned_data
                                )
                                
                        except Exception as e:
                            logger.error(f"Error restoring {sheet_name}: {e}")
                            raise e # Checkpoint: If any sheet fails, everything rolls back
                
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Restore failed, rolled back: {e}")
                raise e
