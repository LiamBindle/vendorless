from vendorless.postgres.database import PostgresDatabase

def test_service_def_1():
    pg = PostgresDatabase()
    for f in pg._template_files():
        print(f)
    print('here')
    