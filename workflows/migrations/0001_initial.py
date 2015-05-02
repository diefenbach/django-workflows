# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='StateInheritanceBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.ForeignKey(verbose_name='Permission', to='permissions.Permission')),
                ('state', models.ForeignKey(verbose_name='State', to='workflows.State')),
            ],
        ),
        migrations.CreateModel(
            name='StateObjectRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_id', models.PositiveIntegerField(null=True, verbose_name='Content id', blank=True)),
                ('content_type', models.ForeignKey(related_name='state_object', verbose_name='Content type', blank=True, to='contenttypes.ContentType', null=True)),
                ('state', models.ForeignKey(verbose_name='State', to='workflows.State')),
            ],
        ),
        migrations.CreateModel(
            name='StatePermissionRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.ForeignKey(verbose_name='Permission', to='permissions.Permission')),
                ('role', models.ForeignKey(verbose_name='Role', to='permissions.Role')),
                ('state', models.ForeignKey(verbose_name='State', to='workflows.State')),
            ],
        ),
        migrations.CreateModel(
            name='Transition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('condition', models.CharField(max_length=100, verbose_name='Condition', blank=True)),
                ('destination', models.ForeignKey(related_name='destination_state', verbose_name='Destination', blank=True, to='workflows.State', null=True)),
                ('permission', models.ForeignKey(verbose_name='Permission', blank=True, to='permissions.Permission', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Name')),
                ('initial_state', models.ForeignKey(related_name='workflow_state', verbose_name='Initial state', blank=True, to='workflows.State', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkflowModelRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_type', models.ForeignKey(verbose_name='Content Type', to='contenttypes.ContentType')),
                ('workflow', models.ForeignKey(related_name='wmrs', verbose_name='Workflow', to='workflows.Workflow')),
            ],
        ),
        migrations.CreateModel(
            name='WorkflowObjectRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_id', models.PositiveIntegerField(null=True, verbose_name='Content id', blank=True)),
                ('content_type', models.ForeignKey(related_name='workflow_object', verbose_name='Content type', blank=True, to='contenttypes.ContentType', null=True)),
                ('workflow', models.ForeignKey(related_name='wors', verbose_name='Workflow', to='workflows.Workflow')),
            ],
        ),
        migrations.CreateModel(
            name='WorkflowPermissionRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.ForeignKey(related_name='permissions', to='permissions.Permission')),
                ('workflow', models.ForeignKey(to='workflows.Workflow')),
            ],
        ),
        migrations.AddField(
            model_name='workflow',
            name='permissions',
            field=models.ManyToManyField(to='permissions.Permission', verbose_name='Permissions', through='workflows.WorkflowPermissionRelation'),
        ),
        migrations.AddField(
            model_name='transition',
            name='workflow',
            field=models.ForeignKey(related_name='transitions', verbose_name='Workflow', to='workflows.Workflow'),
        ),
        migrations.AddField(
            model_name='state',
            name='transitions',
            field=models.ManyToManyField(related_name='states', verbose_name='Transitions', to='workflows.Transition', blank=True),
        ),
        migrations.AddField(
            model_name='state',
            name='workflow',
            field=models.ForeignKey(related_name='states', verbose_name='Workflow', to='workflows.Workflow'),
        ),
        migrations.AlterUniqueTogether(
            name='workflowpermissionrelation',
            unique_together=set([('workflow', 'permission')]),
        ),
        migrations.AlterUniqueTogether(
            name='workflowobjectrelation',
            unique_together=set([('content_type', 'content_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='stateobjectrelation',
            unique_together=set([('content_type', 'content_id', 'state')]),
        ),
    ]
