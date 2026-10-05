# Seed the team members from the company profile PDF.
from django.db import migrations

TEAM = [
    ("Abraham K. Kiptoo", "Chairman of the Board", "0720 997 769", "abkiptoo@gmail.com"),
    ("Premjibhai Pababhai Rangani", "Executive Director", "0721 177 322", "sonia.soniam.ss@gmail.com"),
    ("Joseph Kemboi Kiptoo", "Managing Director", "0728 821 642", "kemboij566@gmail.com"),
    ("Samuel Melly", "Director of International Operations", "+1 267 880 8536", "sam.melly4@gmail.com"),
    ("Joseph Chebii", "Director of Strategic Planning", "+1 360 628 4486", "arapchebii@gmail.com"),
    ("Rants Timothy Ronald", "Director of Business Developments", "+1 360 561 5858", "timothy.rants@gmail.com"),
]


def seed(apps, schema_editor):
    TeamMember = apps.get_model('main', 'TeamMember')
    if TeamMember.objects.exists():
        return
    for order, (name, role, phone, email) in enumerate(TEAM, start=1):
        TeamMember.objects.create(name=name, role=role, phone=phone, email=email, order=order)


def unseed(apps, schema_editor):
    apps.get_model('main', 'TeamMember').objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0002_teammember'),
    ]
    operations = [
        migrations.RunPython(seed, unseed),
    ]
