ORDER_TYPES = [
    ('normal', "Normal Order"),
    ('repair', "Repairs"),
    ('crew_ch', "Crew Change"),
    ('parcel', "Parcels"),
    ('service', "Repair Works")
]

PARCEL_ORDER_TYPES = [
    ('air_in', 'Air/Incoming'),
    ('air_out', 'Air/Outgoing'),
    ('oc_in', 'Ocean/Incoming'),
    ('oc_out', 'Ocean/Outgoing'),
]

CREW_ORDER_TYPES = [
    ('in', 'Embarkation'),
    ('out', 'Disembarkation'),
]

SERVICE_ORDER_TYPES = [
    ('rep', 'Repair'),
]

from . import helpers
from . import res_partner
from . import parcel
from . import crew
from . import service
from . import sale_order
from . import sale_order_batch
from . import purchase_order
from . import egypt_ports
from . import account_invoice