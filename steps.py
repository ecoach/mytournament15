from django.core.urlresolvers import reverse

def steps_nav(user, selected):
    
    all_steps = [
            #'text'         
            #   'styling_class(es)',    
            #       'links_to'
            #           'permission_required'
            #               'selected'
            ['0. New Bracket', 
                '',  
                    reverse('tourney:new_bracket'),
                        'staff',
                            'new_bracket',
            ],
            ['1. Manage Bracket', 
                '',  
                    reverse('tourney:bracket:manage_bracket', kwargs={'bracket': 3}),
                        'staff',
                            'manage_bracket',
            ],
            ['2. Manage Competitors', 
                '',  
                    reverse('tourney:bracket:manage_competitors', kwargs={'bracket': 0}),
                        'staff',
                            'manage_competitors',
            ],
            ['3. Manage Judges', 
                '',  
                    reverse('tourney:bracket:manage_judges', kwargs={'bracket': 0}),
                        'staff',
                            'manage_judges',
            ],
            ['4. Review Bracket', 
                '',  
                    reverse('tourney:bracket:review_bracket', kwargs={'bracket': 0}),
                        'staff',
                            'review_bracket',
            ],
        ]

    steps_nav = []
    for nn in all_steps:
        # style the selected option
        if nn[4] == selected:
            nn[1] = 'current'
        # permission?
        if nn[3] == 'any':
            steps_nav.append(nn)
        elif nn[3] == 'staff' and user.is_staff:
            steps_nav.append(nn)

    return steps_nav

