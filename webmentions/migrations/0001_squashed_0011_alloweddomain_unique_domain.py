# Generated by Django 4.2.18 on 2025-02-07 14:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('webmentions', '0001_initial'), ('webmentions', '0002_outgoingcontent_result_outgoingcontent_tries'), ('webmentions', '0003_alter_incomingwebmention_result'), ('webmentions', '0004_alter_incomingwebmention_result'), ('webmentions', '0005_incomingwebmention_approved'), ('webmentions', '0006_alter_incomingwebmention_options'), ('webmentions', '0007_remove_incomingwebmention_type'), ('webmentions', '0008_alloweddomains'), ('webmentions', '0009_rename_alloweddomains_alloweddomain'), ('webmentions', '0010_alloweddomain_domain'), ('webmentions', '0011_alloweddomain_unique_domain')]

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomingWebmention',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('source', models.URLField(help_text='The URL that mentions the target.')),
                ('target', models.URLField(help_text='The URL that is mentioned by the source.')),
                ('tries', models.PositiveSmallIntegerField(default=0)),
                ('verified', models.BooleanField(default=False)),
                ('source_content', models.TextField(null=True)),
                ('source_content_type', models.CharField(max_length=50, null=True)),
                ('type', models.CharField(choices=[('MENTION', 'Mention'), ('REPLY', 'Reply'), ('LIKE', 'Like'), ('BOOKMARK', 'Bookmark'), ('REPOST', 'Repost')], default='MENTION', max_length=8)),
                ('h_entry', models.JSONField(null=True)),
                ('h_card', models.JSONField(null=True)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('result', models.TextField(blank=True, default='')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='OutgoingContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_url', models.URLField(help_text='The URL with links in the content.')),
            ],
        ),
        migrations.CreateModel(
            name='OutgoingWebmention',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('source', models.URLField(help_text='The URL that mentions the target.')),
                ('target', models.URLField(help_text='The URL that is mentioned by the source.')),
                ('result', models.TextField()),
                ('success', models.BooleanField(default=False)),
                ('tries', models.PositiveSmallIntegerField(default=0)),
            ],
        ),
        migrations.AddConstraint(
            model_name='outgoingwebmention',
            constraint=models.UniqueConstraint(fields=('source', 'target'), name='unique_source_url_per_target_url_outgoingwebmention'),
        ),
        migrations.AddConstraint(
            model_name='outgoingcontent',
            constraint=models.UniqueConstraint(fields=('content_url',), name='unique_content_url'),
        ),
        migrations.AddField(
            model_name='incomingwebmention',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddConstraint(
            model_name='incomingwebmention',
            constraint=models.UniqueConstraint(fields=('source', 'target'), name='unique_source_url_per_target_url_incomingwebmention'),
        ),
        migrations.AddField(
            model_name='outgoingcontent',
            name='result',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='outgoingcontent',
            name='tries',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='incomingwebmention',
            name='result',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='incomingwebmention',
            name='result',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='incomingwebmention',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterModelOptions(
            name='incomingwebmention',
            options={},
        ),
        migrations.RemoveField(
            model_name='incomingwebmention',
            name='type',
        ),
        migrations.CreateModel(
            name='AllowedDomain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(default='', help_text='The domain from which to auto-approve webmentions.', max_length=1000)),
            ],
        ),
        migrations.AddConstraint(
            model_name='alloweddomain',
            constraint=models.UniqueConstraint(fields=('domain',), name='unique_domain'),
        ),
    ]
