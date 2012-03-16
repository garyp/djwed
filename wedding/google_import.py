from djwed.wedding.models import *
from djwed.wedding.utils import *
import csv
import sys,os,string,re,math

# Import Guest/Invitee data from a google docs spreadsheet CSV export


def firstlast_to_guests(first, last, adults):
    adults = int(math.ceil(float(adults)))
    firstel = re.split(" (&|and) ", first)
    lastel = re.split(" (&|and) ", last)
    if len(lastel) == 3 and  len(firstel) == 3 and adults == 2:
        return ((firstel[0],lastel[0]), (firstel[2],lastel[2]))
    elif len(lastel) == 1 and len(firstel) == 1 and adults == 1:
        return ((firstel[0],lastel[0]),)
    elif len(lastel) == 1 and len(firstel) == 3 and adults == 2:
        return ((firstel[0],lastel[0]), (firstel[2],lastel[0]))
    elif len(lastel) == 1 and len(firstel) == 1 and adults == 2:
        return ((firstel[0],lastel[0]),
                ("(Guest of %s %s)"%(first,last), "???"))
    elif len(lastel) == 1 and len(firstel) == 1 and adults == 3:
        return ((firstel[0],lastel[0]),
                ("(Guest 1 of %s %s)"%(first,last), "???"),
                ("(Guest 2 of %s %s)"%(first,last), "???"))
    elif len(lastel) == 1 and len(firstel) == 1 and adults > 3:
        gl = [(firstel[0],lastel[0]),]
        for i in range(1,adults):
            gl.append(("(Guest %d of %s %s)"%(i,first,last), "???"))
        return gl
    else:
        raise Exception("Unsure how to handle {%s;%s;%s}"%(first,last,adults))
        

def google_import(filename, test=False):
    inf = csv.DictReader(open(filename))
    for row in inf:
        if not row["Last Name"]: continue
        if not row["Invite"]: continue

        invite_type = row["Invite"]
        last_name = row["Last Name"]
        first_name = row["First Name"]

        print "\n----"
        print last_name+"; "+first_name

        address = ""
        if row["Other Address"]:
            address = row["Other Address"]
        if row["Home Address"]:
            address = row["Home Address"]
            
        email = row["E-mail Address"]
        if not email and row["E-mail 2 Address"]:
            email = row["E-mail 2 Address"]
        if not email and row["E-mail 3 Address"]:
            email = row["E-mail 3 Address"]

        state = row["Location"]
        if state in ('RU','ES','EE','SE','DE','KR','UAE','UK'):
            country = state
            state = ''
        else:            
            country = 'US'

        assoc = row["Association"]
        if assoc not in map(lambda x: x[0], Invitee.ASSOCIATION_CHOICES):
            raise Exception("Invalid association: '%s'"%(assoc,))

        guestlist = firstlast_to_guests(first_name, last_name, row["Adults"])        
        print guestlist

        full_name_override = None
        #if len(guestlist) > 1:
        #    full_name_override = first_name+" "+last_name

        if test:
            continue

        # Create the database record
        inv = Invitee(full_name_override=full_name_override,
                      invite_code=generate_invite_code(),
                      association=assoc,
                      side=row["Side"],
                      state=state,
                      country=country,
                      full_address=address, 
                      private_notes=row["Notes"])

        if invite_type in ('CA','MA'):
            inv.limited_venue = Venue.objects.get(site=invite_type)

        inv.save()

        InviteeNotes(invitee=inv,
                     likely_site=row["LikelySite"],
                     savedate=row["SaveDate"],
                     adults=row["Adults"] if row["Adults"] else 0,
                     children=row["Kids"] if row["Kids"] else 0,
                     ma_likelihood=row["MA Likelihood"] if row["MA Likelihood"] else 0,
                     ca_likelihood=row["CA Likelihood"] if row["CA Likelihood"] else 0,
                     ).save()

        i = 1
        for g in guestlist:
            guest = Guest(first_name = g[0].strip().decode('utf-8'),
                          last_name = g[1].strip().decode('utf-8'),
                          order = i,
                          nickname = "",
                          email = email,
                          cell_phone = row["Mobile Phone"],
                          home_phone = row["Home Phone"],
                          invitee = inv,
                          role = row["Roles"])
            i+=1
            guest.save()
            print guest

            
if __name__ == "__main__":
    google_import(sys.argv[1])

