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
    montant_ttc: bool = False
    jour_du_mois: int = Field(ge=1, le=28)
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


class SommaireAnnuelReponse(BaseModel):
    annee: int
    mois: list[SommaireMensuelReponse]
    total: SommaireMensuelReponse


class AlerteReponse(BaseModel):
    type: str
    message: str


class TableauDeBordReponse(BaseModel):
    periode: PeriodeReponse
    sommaire: SommaireMensuelReponse
    alertes: list[AlerteReponse]
