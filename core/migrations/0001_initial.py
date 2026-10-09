from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('owner','Owner'),('admin','Admin'),('moderator','Moderator')], default='moderator', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_staff', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Staff Profile'},
        ),
        migrations.CreateModel(
            name='VolunteerEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('location', models.CharField(max_length=300)),
                ('max_volunteers', models.PositiveIntegerField(default=10)),
                ('what_to_bring', models.TextField(blank=True)),
                ('food_type', models.CharField(blank=True, max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Volunteer Event', 'ordering': ['date', 'start_time']},
        ),
        migrations.CreateModel(
            name='VolunteerSignup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField()),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('birthdate', models.DateField()),
                ('school', models.CharField(blank=True, max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signups', to='core.volunteerevent')),
            ],
            options={'verbose_name': 'Volunteer Signup', 'ordering': ['-created_at']},
        ),
        migrations.AlterUniqueTogether(name='volunteersignup', unique_together={('event', 'email')}),
        migrations.CreateModel(
            name='BusinessSignup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('business_name', models.CharField(max_length=200)),
                ('contact_name', models.CharField(max_length=200)),
                ('email', models.EmailField()),
                ('phone', models.CharField(max_length=20)),
                ('business_type', models.CharField(choices=[('restaurant','Restaurant'),('cafe','Cafe / Coffee Shop'),('bakery','Bakery'),('catering','Catering Company'),('grocery','Grocery / Market'),('other','Other')], default='restaurant', max_length=50)),
                ('street_address', models.CharField(max_length=300)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('zip_code', models.CharField(max_length=20)),
                ('frequency', models.CharField(blank=True, max_length=200)),
                ('food_types', models.TextField(blank=True)),
                ('message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Business Partner Signup', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='PodcastEpisode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=300)),
                ('guest_name', models.CharField(max_length=200)),
                ('guest_title', models.CharField(blank=True, max_length=300)),
                ('episode_type', models.CharField(choices=[('video','Video Interview'),('written','Written Interview'),('audio','Audio / Podcast')], default='video', max_length=20)),
                ('description', models.TextField()),
                ('content', models.TextField(blank=True)),
                ('youtube_url', models.URLField(blank=True)),
                ('spotify_url', models.URLField(blank=True)),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='podcast/')),
                ('published_date', models.DateField()),
                ('is_featured', models.BooleanField(default=False)),
            ],
            options={'verbose_name': 'Podcast Episode', 'ordering': ['-published_date']},
        ),
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('role', models.CharField(max_length=200)),
                ('quote', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Testimonial', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='DonationRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('donor_name', models.CharField(blank=True, max_length=200)),
                ('donor_email', models.EmailField(blank=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('method', models.CharField(choices=[('stripe','Stripe'),('zelle','Zelle'),('check','Check'),('other','Other')], max_length=20)),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Donation Record', 'ordering': ['-created_at']},
        ),
    ]
