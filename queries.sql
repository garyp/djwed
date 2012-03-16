

# Extract out-of-town possible attendees for the MA wedding

select last_name, first_name, email, state, country, role from wedding_guest as guest,wedding_invitee as inv 
where guest.invitee_id=inv.id
and ((role!="" and role!="added_by_invitee") or state!="MA")
and guest.id not in (select guest_id from wedding_rsvp where venue_id="MA" and status in ("n","o"))
order by country,state,last_name
;


select last_name, first_name, email, state, country, role from wedding_guest as guest,wedding_invitee as inv 
where guest.invitee_id=inv.id
and (last_name in ("Bitdiddle","Ben") or first_name in ("Alyssa"));


# Debugging/testing actual RSVP information
select last_name, first_name, status, venue_id from wedding_guest left outer join (select * from wedding_rsvp where venue_id="MA") rsvp on wedding_guest.id = rsvp.guest_id order by status; 


# For table selection purposes

select invitee_id, invite_code, association, side, state, country, group_concat(name,",\n"), count(*)
  from wedding_invitee I,
     (select invitee_id, first_name||" "||last_name as name, status
     	      from wedding_guest G, wedding_rsvp R
     	      where guest_id=G.id and status="y" and venue_id="MA") GR
  where I.id=invitee_id
  group by 1;


# Counts by country and state
select country||"  "|| state, sum(num) from wedding_invitee, (select invitee_id, count(*) num from wedding_guest,wedding_rsvp where wedding_guest.id = wedding_rsvp.guest_id and venue_id="MA" and status="y" group by 1) where id=invitee_id group by 1;
