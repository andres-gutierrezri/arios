from django.db import models


class TipoPersona(models.IntegerChoices):
    JURIDICA = 1, 'Persona Jurídica'
    NATURAL = 2, 'Persona Natural'


class RegimenFiscal(models.IntegerChoices):
    RESPONSABLE_IVA = 48, 'Responsable del IVA'
    NO_RESPONSABLE_IVA = 49, 'No responsable del IVA'


class ResponsabilidadesFiscales(models.TextChoices):

    GRAN_CONTRIBUYENTE = 'O-13', 'O-13 Gran contribuyente'
    AUTORRETENEDOR = 'O-15', 'O-15 Autorretenedor'
    AGENTE_RETENCION_IVA = 'O-23', 'O-23 Agente de retención IVA'
    REGIMEN_SIMPLE_TRIBUTACION = 'O-47', 'O-47 Régimen simple de tributación'
    NO_RESPONSABLE = 'R-99-PN', 'R-99-PN No responsable'


class Tributos(models.TextChoices):

    IVA = '01', 'IVA'
    IC = '02', 'IC'
    ICA = '03', 'ICA'
    INC = '04', 'INC'
    RETE_IVA = '05', 'ReteIVA'
    RETE_FUENTE = '06', 'ReteFuente'
    RETE_ICA = '07', 'ReteICA'
    FTO_HORTICULTURA = '20', 'FtoHorticultura'
    TIMBRE = '21', 'Timbre'
    BOLSAS = '22', 'Bolsas'
    IN_CARBONO = '23', 'INCarbono'
    IN_COMBUSTIBLE = '24', 'INCombustibles'
    SOBRETASA_COMBUSTIBLES = '25', 'Sobretasa Combustibles'
    SORDICOM = '26', 'Sordicom'
    NO_CAUSA = 'ZY', 'No causa'
    # PERSONALIZADO = 'ZZ', 'Nombre de la figura tributaria'  # Personalizado


