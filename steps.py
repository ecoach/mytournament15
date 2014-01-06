from django.core.urlresolvers import reverse

def steps_nav(user, selected, bid=-1):
    
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
            ['1. Choose Bracket', 
                '',  
                    reverse('tourney:choose_bracket'),
                        'staff',
                            'choose_bracket',
            ],
            ['2. Manage Bracket', 
                '',  
                    reverse('tourney:bracket:manage_bracket', kwargs={'bracket': bid}),
                        'staff',
                            'manage_bracket',
            ],
            ['3. Manage Competitors', 
                '',  
                    reverse('tourney:bracket:manage_competitors', kwargs={'bracket': bid}),
                        'staff',
                            'manage_competitors',
            ],
            ['4. Manage Judges', 
                '',  
                    reverse('tourney:bracket:manage_judges', kwargs={'bracket': bid}),
                        'staff',
                            'manage_judges',
            ],
            ['5. Review Bracket', 
                '',  
                    reverse('tourney:bracket:review_bracket', kwargs={'bracket': bid}),
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

