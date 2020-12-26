import uuid
from zineb.models import fields, migrations
class Migration:
    def migrate(self):
        model = """
        from zineb.models import fields, migrations
        import uuid

        class Migration(migrations.Migrations):
            operations = [

            ]
        """
        with open('0001_initial.py', mode='w') as f:
            f.write(model.strip())

Migration().migrate()


# class Migration(migrations.Migration):
#     operations = [
#         migrations.RegisterFields(
#             operation_id=uuid.uuid4(),
#             fields=[
#                 fields.UrlField(max_length=40),
#                 fields.CharField(max_length=50)
#             ]
#         )
#     ]
