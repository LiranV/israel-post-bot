from datetime import datetime
import models


class PackagesDAO:
    def __init__(self):
        self.packages = models.Packages

    def update_package(self, user_id, tracking_id, tracking_text):
        package, is_created = self.packages.create_or_get(user=user_id,
                                                          tracking_id=tracking_id.upper(),
                                                          tracking_text=tracking_text,
                                                          update_time=datetime.now())
        if not is_created:
            package.tracking_text = tracking_text
            package.update_time = datetime.now()
            package.save()

    def get_tracking_id_list(self, user_id):
        ids_list = []
        packages = self.packages.select(self.packages.tracking_id).where(
            self.packages.user == user_id).order_by(self.packages.update_time.desc())
        for package in packages:
            ids_list.append(package.tracking_id)
        return ids_list
