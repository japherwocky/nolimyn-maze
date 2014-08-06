

#we're passing all mob flags in, as a dictionary -
#optional args, will not exist, and sorry for the one letter name
def convert_to_diku(a):
    foo = ''


    ########        REQUIRED FLAGS

    
    #might need to take out the spaces
    #also note: long_descr and description always end in \n
    foo += "#%d\n%s~\n%s~\n%s~\n%s~\n" % \
    (a['vnum'],a['name'],a['short_descr'],a['long_descr'],a['description'])

    #racename = race_table[pMobIndex->race].name)
    foo += "%d %d %d %s~\n" % (a['alignment'],a['group'],a['xp_mod'],a['race_name'])

    #in a 7d8, 7 is the _num and 8 is the _type
    #attack is: attack_table[pMobIndex->dam_type].name)
    #hit_dice are.. number of attacks?
    foo += "%d %dd%d+%d %dd%d+%d %d %d %s\n" % \
    (a['level'],a['hit_num'],a['hit_type'],a['hit_bonus'],a['dam_num'],a['dam_type'],a['dam_bonus'],a['hitroll'],a['dam_mod'],a['attack'])

    #AC
    foo += '%d %d %d %d\n' % (a['ac_pierce'],a['ac_bash'],a['ac_slash'],a['ac_exotic'])

    foo += '%(start_pos)s %(sex)s %(wealth)s\n' % (a['start_pos'],a['sex'],a['wealth'])


    """
        copy_vector(dummy, pMobIndex->form);
        BITWISE_XAND(dummy, race_data_lookup(pMobIndex->race)->form);
        copy_vector(dummy2, pMobIndex->parts);
        BITWISE_XAND(dummy2, race_data_lookup(pMobIndex->race)->parts);

        fprintf(fp,"%s %s %s\n", bitvector_to_flag(dummy), bitvector_to_flag(dummy2),
        size_table[UMAX(pMobIndex->size,0)].name);
    """

    foo += '%(form)s %(parts)s %(size)s\n' % (a['form'],a['parts'],a['size'])

    ########            OPTIONAL FLAGS (I THINK)


    #ahh, ok, for all these FOR loop strings, there can be multiples of that line,
    #so these args should all get passed in as LISTS, if passed at all
    """ for(i = 0; i < (32 * MAX_BITVECTOR); i++)
            if(IS_SET(pMobIndex->act, i) && !IS_SET(race_data_lookup(pMobIndex->race)->act, i))
                fprintf(fp,"ACT %s\n",(upstring(flag_name_lookup(i, act_flags))));"""
    try:
        for action in a['behaviors']: foo += 'ACT %s\n' % (action)
    except: pass

    """ for(i = 0; i < (32 * MAX_BITVECTOR); i++)
            if(IS_SET(pMobIndex->off_flags,i) && !IS_SET(race_data_lookup(pMobIndex->race)->off,i))
                fprintf(fp,"OFF %s\n",(upstring(flag_name_lookup(i, off_flags))));"""

    #uh.. is this like.. what the mob is offensive to?
    try:
        for off in a['offs']: foo += 'OFF %s\n' % (off)
    except: pass


    """ for(i = 0; i < (32 * MAX_BITVECTOR); i++)
            if(IS_SET(pMobIndex->affected_by, i) && !IS_SET(race_data_lookup(pMobIndex->race)->aff,i))
                fprintf(fp,"AFF %s\n",(upstring(flag_name_lookup(i, affect_flags)))); """
    #what is an aff?
    try:
        for aff in a['affs']: foo += 'AFF %s\n' % (aff)
    except: pass


    """
        for(i = 0; i < (32 * MAX_BITVECTOR); i++)
            if(IS_SET(pMobIndex->imm_flags, i) && !IS_SET(race_data_lookup(pMobIndex->race)->imm,i))
                fprintf(fp,"IMM %s\n",(upstring(flag_name_lookup(i, imm_flags)))); """

    try:
        for imm in a['immunities']: foo += 'IMM %s\n' % (imm)
    except: pass

    """ for(i = 0; i < (32 * MAX_BITVECTOR); i++)
            if(IS_SET(pMobIndex->res_flags, i) && !IS_SET(race_data_lookup(pMobIndex->race)->res,i))
                fprintf(fp,"RES %s\n",(upstring(flag_name_lookup(i, imm_flags))));"""
    try:
        for res in a['resists']: foo += 'RES %s\n' % (res)
    except: pass
                
    """    for(i = 0; i < (32 * MAX_BITVECTOR); i++)
            if(IS_SET(pMobIndex->vuln_flags, i) && !IS_SET(race_data_lookup(pMobIndex->race)->vuln,i))
                fprintf(fp,"VUL %s\n",(upstring(flag_name_lookup(i, imm_flags))));
    """
    try:
        for vul in a['vulns']: foo += 'VUL %s\n' % (vul)
    except: pass

    """	if (pMobIndex->Class()->GetIndex() != CLASS_NONE) {
                    fprintf(fp,"CLASS %s ", (RSTR)pMobIndex->Class()->name);
                    switch(pMobIndex->Class()->GetIndex()) {
                            case(CLASS_WARRIOR):
                                    styles = 0;
                                    for(i=1; i<MAX_STYLE; i++)
                                            if(IS_SET(pMobIndex->styles, style_table[i].bit)) {
                                                    styles++;
                                                    fprintf(fp, "%s ",style_table[i].name);
                                            }
                                    for(;styles < 2; styles++) {
                                            fprintf(fp, "none ");
                                    }
                                    break;
                            case(CLASS_SORCERER):
                                    fprintf(fp,"%s %s",sphere_table[pMobIndex->ele_major].name,
                                            sphere_table[pMobIndex->ele_para].name);
                                    break;
                    }
                    fprintf(fp,"\n");
            }"""

    try: strclass
    except: strclass = ''
    #SO - if you make a warrior, you need to make two empty style vars: none none
    if (strclass == 'warrior'):
        #maybe try: this, and if styles doesn't exist, except: to double none
        for i in range(2-len(styles)):
            styles.append('none')

        for style in styles:
            strclass += ' %s' % (style)

    #sorcerers must have a major and para element
    elif (strclass == 'sorcerer'):
        strclass += ' %s %s' % (major,para)
        
    if strclass: foo += 'CLASS %(strclass)s\n' % (strclass)

    """	if(pMobIndex->restrict_low != -1 && pMobIndex->restrict_high != 65535)
                    fprintf(fp,"LIMIT %d %d\n",pMobIndex->restrict_low,pMobIndex->restrict_high);"""
    #limits needs to come in as a tuple
    try: foo+= 'LIMIT %d %d\n' % (a['limits'][0],a['limits'][1])
    except:pass

    """	if(pMobIndex->attack_yell)
                    fprintf(fp,"YELL %s~\n", pMobIndex->attack_yell);"""
    try: foo+= 'YELL %s~\n' % (a['yell'])
    except:pass

    """	if(pMobIndex->cabal)
                    fprintf(fp,"CABAL %s\n", cabal_table[pMobIndex->cabal].name);"""
    try: foo+= 'CABAL %s\n' % (a['cabal'])
    except:pass

    """	if (pMobIndex->notes)
                    fprintf(fp,"NOTES %s~\n", pMobIndex->notes);"""
    #uhh.. ok.  notes?
    try: foo+= 'NOTES %s~\n' % (notes)
    except:pass


    """	if (pMobIndex->barred_entry) {
                    switch(pMobIndex->barred_entry->comparison) {
                            case(BAR_EQUAL_TO):
                                    sprintf(buf,"EQUALTO");
                                    break;
                            case(BAR_LESS_THAN):
                                    sprintf(buf,"LESSTHAN");
                                    break;
                            case(BAR_GREATER_THAN):
                                    sprintf(buf,"GREATERTHAN");
                                    break;
                    }
                    switch(pMobIndex->barred_entry->msg_type) {
                            case(BAR_SAY):
                                    sprintf(buf2,"SAY");
                                    break;
                            case(BAR_EMOTE):
                                    sprintf(buf2,"EMOTE");
                                    break;
                            case(BAR_ECHO):
                                    sprintf(buf2,"ECHO");
                                    break;
                    }
                    fprintf(fp,"B %s %s %d %d %s %s~\n%s%s",
                            flag_name_lookup(pMobIndex->barred_entry->type, criterion_flags),
                            buf,
                            pMobIndex->barred_entry->value,
                            pMobIndex->barred_entry->vnum,
                            buf2,
                            pMobIndex->barred_entry->message,
                            
                            (pMobIndex->barred_entry->message_two
                            && pMobIndex->barred_entry->msg_type == BAR_ECHO) ? 
                                    pMobIndex->barred_entry->message_two : "",
                                    
                            (pMobIndex->barred_entry->message_two
                            && pMobIndex->barred_entry->msg_type == BAR_ECHO) ?
                                    "~\n" : "");
            } """
    #yeah.. not sure how the hell this works.  I guess, pass in barentry as a dict
    try:
        b = a['barentry']
        barstr = ''
        barstr += 'B %s %s %d' % (b['criterion'], b['comparison'], b['value'])

        #vnum of.. the room it's blocking access to?  must be
        #msg_type can be say, emote, or echo.  msg2 is probably the first person emote.
        try: b['msg2'] += '\n'
        except: b['msg2'] = ''
        barstr += '%d %s %s~\n%s' % (b['vnum'], b['msg_type'], b['msg1'], b['msg2'])
    except:pass

        

    """	for (i = 0; i < MAX_MOB_AFFECT; i++)
                    if (pMobIndex->affect_sn[i] > -1) 
                            fprintf(fp,"A '%s' %s\n",skill_table[pMobIndex->affect_sn[i]].name,
                                    flag_name_lookup(pMobIndex->affect_bit[i],affect_flags));"""

    #not sure what the diff is between this and AFF up above.  pass in affects as a list of tuples.
    try:
        for aff in a['affects']: foo += "A '%s' %s\n" % (aff[0],aff[1])
    except: pass
            
    """	for (i = 0; i < MAX_MOB_CAST; i++)
                    if (pMobIndex->cast_spell[i])
                            fprintf(fp,"C '%s'\n", pMobIndex->cast_spell[i]);"""

    try:
        for cast in a['casts']: foo += 'C %s\n' % (cast)
    except: pass

    """	for (i = 0; i < MAX_PROFS_TAUGHT_BY_MOB; i++)
                    if (pMobIndex->profs_taught[i] > -1)
                            fprintf(fp, "TEACHES %s~\n", prof_table[pMobIndex->profs_taught[i]].name);"""
    try:
        for cast in a['casts']: foo += 'C %s\n' % (cast)
    except: pass

    return foo


    #um.  I'll implement this when I need it.
    """
            if (pMobIndex->speech) {
                    SPEECH_DATA *sptr;
                    LINE_DATA *lptr;
                    
                    for (sptr = pMobIndex->speech; sptr; sptr = sptr->next) {
                            fprintf(fp,"SPEECH %s\n", sptr->name);
                            for (lptr = sptr->first_line; lptr; lptr = lptr->next)
                                    fprintf(fp,"LINE %d %s %s~\n",
                                            lptr->delay,
                                            flag_name_lookup(lptr->type,speech_table),
                                            lptr->text);
                            fprintf(fp,"END\n");
                    }
            }

            return;
    }
    """


    """
    for nolimud:
    class body:
        def __init(self,stats={},affs=[],inventory=[],gear={},skills=[])


        where affs is a list of aff objects, inventory is a list of item objs, gear
        is a dict of slot:item objs, skills is a list of skill objs
    """

