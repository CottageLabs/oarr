from portality.models import Account
import uuid

if __name__ == "__main__":
    import argparse, getpass
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-n", "--name", help="name of third party organisation")
    parser.add_argument("-c", "--contactname", help="name of contact at third party organisation")
    parser.add_argument("-e", "--contactemail", help="email of contact at third party organisation")
    parser.add_argument("-r", "--register", action="store_true", help="does the user have register access")
    parser.add_argument("-s", "--stats", action="store_true", help="does the user have stats access")
    parser.add_argument("-a", "--admin", action="store_true", help="does the user have admin section access")
    
    args = parser.parse_args()
    
    if not args.name:
        print "Please specify a unique third party organisation name with the -n option"
        exit()
    
    name = args.name
    cname = args.contactname
    cemail = args.contactemail
    register = args.register
    stats = args.stats
    admin = args.admin
    
    token = uuid.uuid4().hex
    
    acc = Account.pull_by_name(name)
    if not acc:
        acc = Account()
        acc.set_name(name)
    
    acc.set_contact(cname, cemail)
    acc.allow_registry_access(register)
    acc.allow_statistics_access(stats)
    acc.allow_admin_access(admin)
    acc.set_auth_token(token)
    
    acc.save()
    
    print "auth token set to", token
    
