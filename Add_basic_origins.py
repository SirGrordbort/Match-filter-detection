"""
Adds origins to events in a given eqcorrscan party based on the templates associated with those events

:author: Toby Messerli
:date: 13/2/2020
"""


from eqcorrscan import Party


def add_origins(write, party):
    """
    adds origins to each event in the party and makes this the preferred origin. the origin is the same as the template
    associated with each event but the time is corrected to the time of each event.
        :type write: bool
        :param write: whether to write the party with added origins to a file
        :type party: eqcorrscan Party
        :param party: The party containing the events and corresponding templates

        Note: adds origins to the copy of the party passed in, use a copy if you want
         to keep the original party unaltered
        """
    for fam in party.families:
        #  gets the template from the family
        template = fam.template
        template_st = template.st
        for det in fam.detections:
            # adds the origin with corrected time to the event
            det._calculate_event(template, template_st)
            # ensures the preferred origin id is set so that the get_preferred_origin method can be used on these events
            det.event.preferred_origin_id = det.event.origins[0].resource_id
    if write:
        party.write("party_with_origins.tgz")  # writes the party with the new origins to the specified output location


if __name__ == "__main__":
    party = Party().read("party.tgz")
    party = party.copy()
    add_origins(True, party)
