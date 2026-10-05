# fa-drill does not exist in Font Awesome; use fa-oil-well so the borehole
# card icon actually renders.
from django.db import migrations


def fix(apps, schema_editor):
    HomeServiceCard = apps.get_model('main', 'HomeServiceCard')
    HomeServiceCard.objects.filter(icon='fa-drill').update(icon='fa-oil-well')


def unfix(apps, schema_editor):
    HomeServiceCard = apps.get_model('main', 'HomeServiceCard')
    HomeServiceCard.objects.filter(icon='fa-oil-well').update(icon='fa-drill')


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0005_seed_page_content'),
    ]
    operations = [
        migrations.RunPython(fix, unfix),
    ]
