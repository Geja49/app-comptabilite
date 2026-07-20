from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategorieDepenseBase(BaseModel):
    nom: str = Field(min_length=1, max_length=100)


class CategorieDepenseCreate(CategorieDepenseBase):
    pass


class CategorieDepenseReponse(CategorieDepenseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    est_systeme: bool


class RevenuBase(BaseModel):
    date: date
    nombre_courses: int = Field(ge=0)
    revenu_brut: Decimal = Field(ge=0)
    pourboires: Decimal = Field(ge=0, default=Decimal("0"))


class RevenuCreate(RevenuBase):
    confirmer_modification_passee: bool = False


class RevenuUpdate(RevenuBase):
    confirmer_modification_passee: bool = False


class RevenuReponse(RevenuBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    redevance_gouv: Decimal
    tps_percue: Decimal
    tvq_percue: Decimal
    total_net_encaisse: Decimal


class DepenseBase(BaseModel):
    date: date
    fournisseur: str = Field(min_length=1, max_length=200)
    categorie_id: int
    montant_saisi: Decimal = Field(gt=0)
    saisie_ttc: bool = False


class DepenseCreate(DepenseBase):
    confirmer_modification_passee: bool = False


class DepenseUpdate(DepenseBase):
    confirmer_modification_passee: bool = False


class DepenseReponse(DepenseBase):
    id: int
    montant_ht: Decimal
    tps: Decimal
    tvq: Decimal
    montant_total: Decimal
    categorie_nom: str
    est_recurrente: bool
    depense_recurrente_id: int | None = None


class EntreeKilometrageBase(BaseModel):
    date: date
    odometre_debut: Decimal = Field(ge=0)
    odometre_fin: Decimal = Field(ge=0)
    km_professionnels: Decimal = Field(ge=0)


class EntreeKilometrageCreate(EntreeKilometrageBase):
    confirmer_modification_passee: bool = False


class EntreeKilometrageUpdate(EntreeKilometrageBase):
    confirmer_modification_passee: bool = False


class EntreeKilometrageReponse(EntreeKilometrageBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    km_totaux: Decimal
    taux_pro: Decimal


class DepenseRecurrenteBase(BaseModel):
    fournisseur: str = Field(min_length=1, max_length=200)
    categorie_id: int
    montant: Decimal = Field(gt=0)
    montant_ttc: bool = True
    jour_du_mois: int = Field(ge=1, le=28, default=1)
    frequence: str = Field(default="mensuelle", pattern="^(mensuelle|par_jour_travail)$")
    actif: bool = True


class DepenseRecurrenteCreate(DepenseRecurrenteBase):
    pass


class DepenseRecurrenteUpdate(DepenseRecurrenteBase):
    pass


class DepenseRecurrenteReponse(DepenseRecurrenteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    categorie_nom: str


class PeriodeReponse(BaseModel):
    id: int
    annee: int
    mois: int
    est_passee: bool


class ParametresFiscauxReponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    annee: int
    methode_tps_tvq: str
    frequence_declaration: str = "annuelle"
    tps_taux_reguliere: Decimal
    tvq_taux_reguliere: Decimal
    tps_taux_rapide: Decimal
    tvq_taux_rapide: Decimal
    rabais_rapide_taux: Decimal
    rabais_rapide_plafond: Decimal
    redevance_par_course: Decimal


class ParametresFiscauxUpdate(BaseModel):
    methode_tps_tvq: str = Field(pattern="^(reguliere|rapide)$")
    frequence_declaration: str | None = Field(
        default=None, pattern="^(mensuelle|trimestrielle|annuelle)$"
    )


class SommaireMensuelReponse(BaseModel):
    mois: int
    mois_nom: str
    revenu_brut: Decimal
    tps_percue: Decimal
    tvq_percue: Decimal
    depenses_totales: Decimal
    tps_payee: Decimal
    tvq_payee: Decimal
    tps_a_remettre: Decimal
    tvq_a_remettre: Decimal
    depenses_admissibles_proratees: Decimal
    methode_tps_tvq: str = "reguliere"
    redevance_totale: Decimal = Decimal("0")
    revenu_total_ttc: Decimal = Decimal("0")
    rabais_rapide_applique: Decimal = Decimal("0")


class SommaireAnnuelReponse(BaseModel):
    annee: int
    mois: list[SommaireMensuelReponse]
    total: SommaireMensuelReponse
    methode_tps_tvq: str = "reguliere"
    rabais_rapide_applique: Decimal = Decimal("0")


class AlerteReponse(BaseModel):
    type: str
    message: str


class RappelFiscalReponse(BaseModel):
    impot: str
    type: str
    titre: str
    description: str
    date_limite: str
    jours_restants: int
    urgence: str
    organisme: str
    periode: str


class PointSerieMensuelle(BaseModel):
    mois: int
    mois_nom: str
    ventes: Decimal
    depenses: Decimal
    benefice: Decimal
    jours_travailles: int = 0
    courses: int = 0


class ProductiviteReponse(BaseModel):
    heures_par_jour: Decimal
    jours_travailles: int
    heures_totales: Decimal
    courses: int
    ventes: Decimal
    depenses: Decimal
    benefice: Decimal
    revenu_par_heure: Decimal
    revenu_par_jour: Decimal
    benefice_par_heure: Decimal
    courses_par_heure: Decimal
    ratio_depenses: Decimal
    marge_benefice: Decimal


class TableauDeBordReponse(BaseModel):
    periode: PeriodeReponse
    sommaire: SommaireMensuelReponse
    alertes: list[AlerteReponse]
    rappels_fiscaux: list[RappelFiscalReponse] = []
    serie_mensuelle: list[PointSerieMensuelle] = []
    productivite: ProductiviteReponse | None = None
