from datetime import datetime
import models


class PackagesDAO:
    def __init__(self):
        self.packages = models.Packages

    def update_package(self, user_id, tracking_id, tracking_text):
        try:
            package = self.packages.get(self.packages.user == user_id,
                                        self.packages.tracking_id == tracking_id)
            package.tracking_text = tracking_text
            package.update_time = datetime.now()
            package.save()

        except self.packages.DoesNotExist:
            self.packages.create(user=user_id,
                                 tracking_id=tracking_id,
                                 tracking_text=tracking_text,
                                 update_time=datetime.now())

    def get_tracking_id_list(self, user_id):
        ids_list = []
        packages = self.packages.select(self.packages.tracking_id).where(
            self.packages.user == user_id).order_by(self.packages.update_time.desc())
        for package in packages:
            ids_list.append(package.tracking_id)
        return ids_list

    def delete_package(self, user_id, tracking_id):
        package = self.packages.get((self.packages.user == user_id) & (self.packages.tracking_id == tracking_id))
        return package.delete_instance()
