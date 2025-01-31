from random import choice
import random
import forgery_py

from .base import FakeDataGenerator

from assets.models import *
from assets.const import AllTypes


class NodesGenerator(FakeDataGenerator):
    resource = 'node'

    def do_generate(self, batch, batch_size):
        nodes_to_generate_children = list(Node.objects.all())
        for i in batch:
            parent = random.choice(nodes_to_generate_children)
            parent.create_child()


class PlatformGenerator(FakeDataGenerator):
    resource = 'platform'
    category_type: dict
    categories: list

    def pre_generate(self):
        self.category_type = dict(AllTypes.category_types())
        self.categories = list(self.category_type.keys())

    def do_generate(self, batch, batch_size):
        platforms = []
        for i in batch:
            category = choice(self.categories)
            tp = choice(self.category_type[category].choices)
            data = {
                'name': forgery_py.name.company_name(),
                'category': category,
                'type': tp[0]
            }
            platforms.append(Platform(**data))
        Platform.objects.bulk_create(platforms, ignore_conflicts=True)


class AssetsGenerator(FakeDataGenerator):
    resource = 'asset'
    node_ids: list
    platform_ids: list

    def pre_generate(self):
        self.node_ids = list(Node.objects.all().values_list('id', flat=True))
        self.platform_ids = list(Platform.objects.all().values_list('id', flat=True))

    def set_assets_nodes(self, assets):
        for asset in assets:
            nodes_id_add_to = random.sample(self.node_ids, 3)
            asset.nodes.add(*nodes_id_add_to)

    def do_generate(self, batch, batch_size):
        assets = []

        for i in batch:
            ip = forgery_py.internet.ip_v4()
            hostname = forgery_py.email.address().replace('@', '.')
            hostname = f'{hostname}-{ip}'
            data = dict(
                ip=ip,
                name=hostname,
                platform_id=choice(self.platform_ids),
                created_by='Fake',
                org_id=self.org.id
            )
            assets.append(Asset(**data))
        creates = Asset.objects.bulk_create(assets, ignore_conflicts=True)
        self.set_assets_nodes(creates)

    def after_generate(self):
        pass
