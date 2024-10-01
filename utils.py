# utils.py
from models import User, Package

def show_friends(user):
    print(f"{user.username}'s friends: {[f.username for f in user.friends]}")

def get_package_hierarchy(package_id, root_user_id):
    root_user = User.query.get(root_user_id)
    hierarchy = {'name': root_user.username, 'children': []}
    root_package = Package.query.filter_by(id=package_id).first()
    image_id = root_package.content_id

    def build_hierarchy(user_id):
        children = []
        packages = Package.query.filter_by(content_id=image_id, sender_id=user_id).all()
        for package in packages:
            recipient = User.query.get(package.recipient_id)
            child_hierarchy = {'name': recipient.username, 'children': build_hierarchy(recipient.id)}
            children.append(child_hierarchy)
        return children

    hierarchy['children'] = build_hierarchy(root_user_id)
    return hierarchy