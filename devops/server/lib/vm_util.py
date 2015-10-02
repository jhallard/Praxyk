#!/bin/env python
import digitalocean


class vmUtil :

    def __init__(self, vmargs) :
        self.tok = vmargs['tok']
        self.manager = None # will be filled on @login call

    def login(self, vendor="DO") :
        self.manager = digitalocean.Manager(token=self.tok)

        status = 'f' if not self.manager else 's'
        return self.logger(self.logclient, 'IAAS VENDOR LOGIN', status, ['Vendor'], vendor)

    def get_vm_instances(self, vendor="DO") :
        if self.manager :
            self.logger(self.logclient, 'GET VM INSTANCES', 's', ['Vendor'], vendor)
            return self.manager.get_all_droplets()
        else :
            self.logger(self.logclient, 'GET VM INSTANCES', 'f', ['Vendor'], vendor)
            return None

    def get_vm_instance(self, id) :
        if self.manager :
            return self.manager.get_droplet(id)
        return None

    def get_boot_images(self) :
        if self.manager :
            imgs = self.manager.get_images()
            return [self.format_image(img) for img in imgs]

    def get_custom_images(self) :
        if self.manager :
            imgs = self.manager.get_images(private=True)
            return [self.format_image(img) for img in imgs]


    def format_do_instance(self, instance, creator) :
        return {
                "name" : instance.name,
                 "id"   : instance.id,
                 "ip"   : instance.ip_address,
                 "ipv6" : instance.ip_v6_address,
                 "class": instance.size_slug,
                 "disk" : instance.disk,
                 "status": instance.status,
                 "creator": creator,
                 "created_at": self.format_time_str(str(instance.created_at)),
                 "provider" : "DO",
                 "image_ids" : instace.snapshot_ids,
                 "backup_ids": instance.backup_ids
             }

    def format_ssh_key(self, key) :
        return {
                "id": key.id,
                 "name": key.name,
                 "pubkey": key.pubkey,
                 "fingerprint": key.fingerprint,
                 }

    def format_image(self, image) :
        return {
                "id" : image.id,
                "name" : image.name
                }


