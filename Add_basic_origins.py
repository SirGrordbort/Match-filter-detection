from eqcorrscan import Party

def add_origins(write, party):
    for fam in party.families:
        template = fam.template
        template_st = template.st
        for det in fam.detections:
            det._calculate_event(template, template_st)
        if write:
            party.write("party_with_origins.tgz")

if __name__ == "__main__":
    party = Party().read("party.tgz")
    add_origins(True, party)