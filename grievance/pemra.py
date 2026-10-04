"""Council locations from PEMRA's current Council directory, reviewed 2026-10-04.

Regional offices are not assumed to be separately constituted Councils. Older
newsletters mention Multan, but the current Council directory lists five seats.
"""
SOURCE = "https://www.pemra.gov.pk/coc/"
REVIEWED = "2026-10-04"
OFFICE_SOURCE = "https://www.pemra.gov.pk/contact/"
OFFICES = {
    "pemra-gujranwala": dict(region="Punjab", city="Gujranwala", phone="055-9330021-22"),
    "pemra-faisalabad": dict(region="Punjab", city="Faisalabad", phone="041-9330411"),
    "pemra-sargodha": dict(region="Punjab", city="Sargodha", phone="048-9330166"),
    "pemra-multan": dict(region="Punjab", city="Multan", phone="061-9210220"),
    "pemra-hyderabad": dict(region="Sindh", city="Hyderabad", phone="022-2780309"),
    "pemra-sukkur": dict(region="Sindh", city="Sukkur", phone="071-9310450"),
    "pemra-peshawar-north": dict(region="Khyber Pakhtunkhwa", city="Peshawar North", phone="091-9216355"),
}
COUNCILS = {
    "pemra-lahore": dict(region="Punjab", city="Lahore", council="Punjab",
        address="319-A, Upper Mall Scheme, Lahore", phone=""),
    "pemra-karachi": dict(region="Sindh", city="Karachi", council="Sindh",
        address="House # D-71, Block-7, Boat Basin, Clifton, Karachi", phone="021-99332255"),
    "pemra-peshawar": dict(region="Khyber Pakhtunkhwa", city="Peshawar", council="Khyber Pakhtunkhwa",
        address="5th Floor, Workers Welfare Board Building, Phase-5, Hayatabad, Peshawar", phone="091-9216590"),
    "pemra-quetta": dict(region="Balochistan", city="Quetta", council="Balochistan",
        address="House No. 53/2, Zarghoon Road, Quetta Cantt.", phone="081-9201199"),
    "pemra-islamabad": dict(region="Islamabad", city="Islamabad", council="Islamabad",
        address="PEMRA Headquarters, Sector G-8/1, Mauve Area, Islamabad", phone="051-9107133"),
}


def is_pemra(department_id):
    return department_id == "pemra" or department_id in COUNCILS or department_id in OFFICES


def council_id(region):
    return next((id for id, c in COUNCILS.items() if c["region"] == region), None)


def recipient(council):
    return (f"Regional Director, PEMRA {council['city']} / "
            f"Secretary, Council of Complaints {council['council']}")
