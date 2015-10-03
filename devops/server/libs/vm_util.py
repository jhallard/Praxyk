#!/bin/env python
import digitalocean


class vmUtil :

    def __init__(self, vmargs) :
        self.tok = vmargs['tok']
        self.logger = vmargs['logutil']
        self.logclient = vmargs['logclient']
        self.manager = None # will be filled on @login call

    def login(self, vendor="DO") :
        self.manager = digitalocean.Manager(token=self.tok)

        status = 'f' if not self.manager else 's'
        return self.logger.log_event(self.logclient, 'IAAS VENDOR LOGIN', status, ['Vendor'], vendor)

    def get_vm_instances(self, vendor="DO") :
        self.logger.log_event(self.logclient, 'GET VM INSTANCES', 'a')
        if self.manager :
            try :
                self.logger.log_event(self.logclient, 'GET VM INSTANCES', 's', ['Vendor'], vendor)
                return self.manager.get_all_droplets()
            except Exception, e :
                self.logger.log_event(self.log_client, "GET VM INSTANCES", 'e', ['Vendor', 'e.what()'], (vendor, str(e)))
                return None
        else :
            self.logger.log_event(self.logclient, 'GET VM INSTANCES', 'f', ['Vendor'], vendor)
            return None

    def get_vm_instance(self, id) :
        self.logger.log_event(self.logclient, 'GET VM INSTANCE', 'a', ['Instance Id'], id)
        if self.manager :
            try : 
                inst = self.manager.get_droplet(id)
                if inst :
                    self.logger.log_event(self.logclient, 'GET VM INSTANCE', 's', ['Instance Id'], id)
                    return inst
            except Exception, e :
                self.logger.log_event(self.log_client, "GET VM INSTANCE", 'e', ['Instance Id', 'e.what()'], (id, str(e)))
                return None

        self.logger.log_event(self.logclient, 'GET VM INSTANCE', 'f', ['Instance Id'], id)
        return None

    def get_boot_images(self) :
        self.logger.log_event(self.logclient, 'GET BOOT IMAGES', 'a')
        if self.manager :
            try : 
                imgs = self.manager.get_images()
                imgs = [self.format_image(img) for img in imgs]
                self.logger.log_event(self.logclient, 'GET BOOT IMAGES', 's', ['#Images'], str(len(imgs)) )
                return imgs
            except Exception, e :
                self.logger.log_event(self.log_client, "GET BOOT INSTANCE", 'e', ['e.what()'], (str(e)))
                return None

        else :
            self.logger.log_event(self.logclient, 'GET BOOT IMAGES', 'f', ['self.manager'], 'Null')
            return None

    def get_custom_images(self) :
        self.logger.log_event(self.logclient, 'GET CUSTOM IMAGES', 'a')
        if self.manager :
            imgs = self.manager.get_images(private=True)
            if imgs :
                self.logger.log_event(self.logclient, 'GET CUSTOM IMAGES', 's', ['Num Images'], len(imgs))
                return [self.format_image(img) for img in imgs]
            return  self.logger.log_event(self.logclient, 'GET CUSTOM IMAGES', 'f', [], "", "Images came back Null")

    def create_vm_snapshot(self) :
        pass

    def create_vm_image(self) :
        pass



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


