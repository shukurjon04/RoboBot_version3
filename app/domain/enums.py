from enum import StrEnum, auto

class UserStatus(StrEnum):
    NEW = auto()
    WAIT_CHANNEL = auto()
    WAIT_SURVEY = auto()
    ACTIVE = auto()
    BLOCKED = auto()


class ReferralStatus(StrEnum):
    PENDING = auto()
    CONFIRMED = auto()

class Region(StrEnum):
    TOSHKENT_SHAHRI = "Toshkent shahri"
    TOSHKENT_VILOYATI = "Toshkent viloyati"
    ANDIJON = "Andijon viloyati"
    BUXORO = "Buxoro viloyati"
    FARGONA = "Farg'ona viloyati"
    JIZZAX = "Jizzax viloyati"
    XORAZM = "Xorazm viloyati"
    NAMANGAN = "Namangan viloyati"
    NAVOIY = "Navoiy viloyati"
    QASHQADARYO = "Qashqadaryo viloyati"
    QORAQALPOGISTON = "Qoraqalpog'iston Respublikasi"
    SAMARQAND = "Samarqand viloyati"
    SIRDARYO = "Sirdaryo viloyati"
    SURXONDARYO = "Surxondaryo viloyati"
class AgeRange(StrEnum):
    KIDS = "6-10 yosh"
    PRE_TEENS = "10-15 yosh"
    TEENS = "16 - 20 yosh"
    ADULTS = "21-25 yosh"
    SENIORS = "26 dan kotta"

class StudyStatus(StrEnum):
    TWO_MONTHS = "ha 2 oylik kursda tahsil olganman"
    FIVE_MONTHS = "ha 5 oylik kursda tahsil olganman"
    NO = "yo'q o'qimaganman"
    OTHER = "boshqa markazda o'qiganman"
