# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 15:23:11 2017

@author: Rignak
"""
keys = ['affirmatif intemporel poli', 'affirmatif passé poli', 'affirmatif intemporel neutre',
        'affirmatif passé neutre', 'progressif intemporel neutre', 'négatif intemporel poli',
        'négatif passé poli', 'négatif intemporel neutre', 'négatif passé neutre',
        'forme inaccomplie', 'forme terminale', 'forme hypothétique', 'forme en TE',
        'forme conjonctive', 'forme attributive', 'forme impérative', 'forme en TA']
verbs = ['écrire', 'demander (un renseignement)', 'travailler', 'nager', 'se dépêcher', 'boire', 'lire', 'se reposer', 'jouer', 'appeler', 'prendre (une photo)', 'abattre', 'retourner', 'se terminer', 'envoyer', 'comprendre', 'entrer', 'attendre', 'tenir', 'acheter', 'aspirer', 'apprendre', 'recevoir', 'parler', 'dormir', 'manger', 'coller', 'apparaître', 'apprendre (qqch à qqn)', 'venir chercher', 'se fatiguer', 'fermer', 'arrêter', 'commencer', 'observer', 'poser', 'emprunter', 'être', 'porter', 'étudier', 'se marier', 'se promener', 'copier']
for key in keys:
    for verb in verbs:
        print(verb+ ' ('+key+')')