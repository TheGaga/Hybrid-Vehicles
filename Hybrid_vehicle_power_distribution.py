# -*- coding: utf-8 -*-
"""
Created on Fr Dec 5 12:51:48 2014

@author: Thomas Galeon

REPARTITION GLOUTONNE DU COUPLE
"""
from __future__ import division
from pylab import *
from math import *


                #########################################
                #                                       #
                #  Constantes, définitions, relations   #
                #                                       #
                #########################################

#Rayon du pneu (m):
R_pneu = 0.29
#Densité de l'air (kg/m^3)
g_air = 1.013
#Coefficient de trainée
C_x = 0.32
#Surface frontale du véhicule (m^2)
S_f = 2.6
#Coefficients de resistance au roulement
a = 0.035
b = 0.0001
#Masse du vehicule (kg): 
M_veh = 1000
#g (acceleration (m/s^2)):
g = 9.81
#Rapports de Boite :
R1 = 12.3
R2 = 6.7
R3 = 4.3
R4 = 3.2
R5 = 2.3
  
#Les différentes Forces :

#Aero : (1/2)*g_air*S_f*C_x*V_veh
#Roul : M_veh *  g * (a+b*(V_veh**2)) * cos(alpha(t))
#Gravitationnel (si pente) : M_veh * g * sin(alpha(t))
#De somme : F_res
#Force de traction (fournie par le moteur): F_trac = F_res + M_veh*(d/dt)V_veh


#Relations

# w_roue = w_moteur/rapport(v)
# V_veh = w_roue * R_pneu
# C_roue = F_trac * R_pneu #(= M_veh * (R_pneu**2)*(d/dt)w_roue * C_res)

#Contrainte physique
#Couple electrique maximum (Nm)
C_max = 50      
      
   
                #########################################
                #                                       #
                #        Fonctions principales          #
                #      - Repartition gloutonne -        #
                #                                       #
                #########################################   
      
   
def repartition(c_tot,c_th,regime,nb_pos,acc,to,t):
    # pour un couple total donne, repartition renvoie la repartition
    # correspondant a la meilleure efficacite
    
    if acc<0:
        return 0,c_tot,1
          
    conso_th = max((puissance_inst(t)),0)*to/(34000000*rendement(c_th,regime))
    eff = 0
    c_el = 0
    best_rend = rendement(c_th,regime)
    cthm = c_tot
    pas = c_tot/nb_pos
    
    for i in range(nb_pos):
        cthm -= pas
        rend_test = rendement(cthm,regime)
        ctest = c_tot - cthm
        batt_ut = 1/11000*(((4*rapport(t)*ctest)/(3*R_pneu))*NEDC(t)/3.6)*to
        P_hyb = (4*rapport(t)*(cthm)/(3*R_pneu))*NEDC(t)/3.6        
        conso_hyb = max(P_hyb,0)*to/(34000000*rend_test)
        if batt_ut == 0:
            # pas de division par zero
            eff_test = 0.0001
        else:
            eff_test = (conso_th-conso_hyb)/batt_ut
        if (eff_test> eff and ctest <= C_max):
            c_el = ctest
            best_rend = rend_test
            eff = eff_test  
            
    return (c_tot-c_el,c_el,best_rend)



def best_recharge(couple,regime,nb_pos):
    # calcule la meilleure recharge de batterie possible pour un couple a
    # fournir donne
    if couple<0:
        return 0,1
    rend_init = rendement(couple,regime)
    test = couple
    res = test
    pas = couple*0.1*(1/nb_pos)
    for i in range(nb_pos):
        rend_test = rendement(test,regime)
        test += pas
        if (rend_test >= rend_init):
            res = test
            rend_res = rend_test
    return res,rend_res


    
def tab_ref(parcours,tdeb,tfin,n):
    # Renvoie l'ensemble des tableaux necessaires a la repartition du couple
    # selon l'efficacite - a savoir la consommation d'essence et de batterie
    # selon le mode de fonctionnement, la recharge possible de batterie
    nb_pos = 10
    duree = tfin-tdeb
    to = duree/n
    tab_batt_ut = []
    tab_recharge_max = []
    tab_eco_essence = []
    tab_best_cel = []
    tab_recharge_cel = []
    tab_conso_recharge = []
    conso_th_seul = []
    tab_conso_hyb = []
    
    for i in range(n):
        t = tdeb + i*to
        #calcul_couple(t)
        c_th = couple_moteur(t)
        
        #Calcul de la meilleure répartition
        reg = regime(t)
        acc = acceleration(t)
        best_c_th,best_c_el,best_rend = repartition(c_th,c_th,reg,nb_pos,acc,to,t)
        
        #Calcul de la batterie utlisée
        c_recharge,rend_recharge = best_recharge(c_th,reg,nb_pos)
        
        #Calcul des consonmmations
        conso_th = max((puissance_inst(t)),0)*to/(34000000*rendement(c_th,reg))
        P_hyb = ((4*rapport(t)*best_c_th)/(3*R_pneu))*NEDC(t)/3.6
        conso_hyb = max(P_hyb,0)*to/(34000000*best_rend)
        P_rech = ((4*rapport(t)*c_recharge)/(3*R_pneu))*NEDC(t)/3.6
        conso_recharge = max(P_rech,0)*to/(34000000*rend_recharge)
    
        #Calcul de la batterie utlisée
        batt_ut = 1/10000*(((4*rapport(t)*best_c_el)/(3*R_pneu))*NEDC(t)/3.6)*to
        batt_rech = -1/11000*(((4*rapport(t)*(c_recharge-c_th)/(3*R_pneu))*NEDC(t)/3.6))*to
        
        #On ajoute dans les listes
        conso_th_seul.append(conso_th)
        tab_best_cel.append(best_c_el)
        tab_eco_essence.append(conso_th - conso_hyb)
        tab_recharge_max.append(batt_rech)
        tab_batt_ut.append(batt_ut)
        tab_recharge_cel.append(c_th-c_recharge)
        tab_conso_recharge.append(conso_recharge)
        tab_conso_hyb.append(conso_hyb)        
        
    return conso_th_seul,tab_eco_essence,tab_conso_hyb,tab_batt_ut, tab_recharge_max,tab_conso_recharge,tab_best_cel,tab_recharge_cel
        
        


# Tri_efficacite retire les elements negatifs (qui ne correspondent pas a une
#economie d'essence ou a la realite physique) et on renvoie la liste triee
#selon l'efficacite   
def tri_efficacite(tab):
    tab.append((0,-1))
    tab.sort()
    indice = tab.index((0,-1))
    neg = tab[:indice]
    pos = tab[(indice+1)::]
    pos.reverse()
    pos.extend(neg)
    return pos


    
def ajoute_list(liste,indice,valeur):
    n=len(liste)
    for i in range(indice,n):
        if liste[i] + valeur > 100:
            diff = 100 - liste[i]
            return ajoute_list(liste,i,diff)
        liste[i] += valeur
    return liste

def trouve_neg(liste):
    n = len(liste)
    for i in range(n):
        if liste[i] < 0:
            return i
    return -1

    
def mise_a_jour(etat1,batt1,recharge1,conso_bat,inst):
    # determination du mode de fonctionnement a l'instant t
    etat = list(etat1)
    batt=list(batt1)
    rech=list(recharge1)
    
    if etat[inst] == False:
        # On utilise deja cet instant pour la recharge
        return etat,batt
    
    ## ON SUPPOSE QUE L'ON TRAVAILLE EN MODE HYBRIDE A L'INSTANT T
    etat[inst] = True
    
    # On met a jour la liste de charge de la batterie
    batt2 = ajoute_list(batt,inst,-conso_bat)
    batt = batt2
    
    # On verifie que l'etat de charge est toujours superieur a 0, si ce n'est
    # pas le cas on utilise des instants precedents pour recharger la batterie
    
    # On regarde si il existe un instant tel que l'etat de charge soit negatif 
    ind_neg = trouve_neg(batt)
    
    while ind_neg != -1:
        
        # On se sert d'instants precedents pour recharger
        ind_rech = ind_neg - 1
        while ind_rech >= 0 and batt[ind_neg]<0:
            if etat[ind_rech] == None:
                etat[ind_rech] = False
                batt2 = ajoute_list(batt,ind_rech,rech[ind_rech])
                batt = batt2
            ind_rech -= 1
            
        # On verifie qu'on a pu recharger la batterie pour l'instant ind_neg,
        # si ce n'est pas le cas ON N'UTILISE PAS LE MODE HYBRIDE A L'INSTANT
        # INST
            if batt[ind_neg] < 0:
                return etat1,batt1
        
        # On verifie que la charge est positive a chaque instant, sinon on
        # refait un passage de boucle        
        ind_neg = trouve_neg(batt)
    
    # LE MODE HYRBIDE EST POSSIBLE A L'INSTANT T    
    return etat,batt    




def repartition_gloutonne(parcours,tdeb,tfin,chargedeb,n):
    # Algorithme principal renvoyant la repartition du couple par methode
    # gloutonne sur le NCEC. n est le nombre de points consideres
    
    # calcul des donnees necessaires a la repartition du couple
    conso_th,eco,conso_hyb,conso_bat,rech_pos,conso_rech,couple_el_hyb,couple_el_rech = tab_ref(parcours,tdeb,tfin,n)
    
    # Au depart on dispose de chargedeb % de batterie
    charge = [chargedeb]*n
    
    ## CALCUL DE L'EFFICACITE POUR CHAQUE INSTANT
    
    # Efficacite est une liste de couple (i,e) avec i l'instant et e 
    # l'efficacite a l'instant i 
    efficacite = []
    
    for i in range(n):
        if conso_bat[i] == 0:
            efficacite.append((0,i))
        else:
            efficacite.append((eco[i]/conso_bat[i],i))
    
    # Efficacite2 correspond a la liste des efficacites (elle sert a la 
    # representation graphique) - le 20000 sert pour la representation
    # graphique
    efficacite2 = [20000 * x for (x,y) in efficacite]


    ## METHODE GLOUTONNE POUR LA REPARTITION DU COUPLE    
    # Tri des efficacites par ordre decroissant
    efficacite = tri_efficacite(efficacite)
    
    # Etat est une liste indiquant le mode de fonctionnement du vehicule
    # (hybride, thermique seul ou regeneration)
    # Au depart on ne sait pas quand utiliser l'hybridation
    etat = [None]*n
    
    # Determination du mode de fonctionnement pour chaque instant
    for i in range(n):
        (e,inst) = efficacite[i]
        # Determinantion du mode de fonctionnement a l'instant inst et mise
        # a jour des etats et de la charge
        (etat_new,charge_new) = mise_a_jour(etat,charge,rech_pos,conso_bat[inst],inst)
        etat = etat_new
        charge = charge_new
        
        
    ## REPRESENTATION DE LA REPARTITION DU COUPLE SOUS FORME DE LISTE ET CALCUL
    ## DE LA CONSOMMATION TOTALE EN MODE THERMIQUE SEUL OU EN MODE HYBRIDE
      
    # Consommation en mode thermique seul  
    conso_th_tot = 0
    # Consommation en mode hybride
    conso_tot = 0
    
    # Liste des couples a fournir a chaque instant
    couple_el = []
    couple_th = []
    
    to = (tfin-tdeb)/n    
    
    for j in range(n):
        
        # Calcul de la consommation sans hybridation
        conso_th_tot += conso_th[j]

        couple_tot = couple_moteur(tdeb + j*to)
                
        # Calcul de la consommation totale avec hybridation
        if etat[j] == False:
            # On travaille alors en recharge
            conso_tot += conso_rech[j]
            cel = couple_el_rech[j]
            
        if etat[j] == None:
            #On travaille en mode thermique
            conso_tot += conso_th[j]
            cel = 0           
            
        if etat[j] == True:
            #On travaille en mode hybride
            conso_tot += conso_hyb[j]
            cel = couple_el_hyb[j]          
        
        # Couple electriqe et thermique a fournir a l'instant i
        couple_el.append(cel)
        couple_th.append(couple_tot - cel)
    

    ## TRACE DES COURBES    
    
    temps = [tdeb + i*to for i in range(n)]
    vitesse = [NEDC(tdeb + i*to) for i in range(n)]
    
    plot(temps,charge,'g:',label = "Etat de charge (%)",linewidth=5)
    plot(temps,vitesse,'black',label = "Vitesse du vehicule (km/h)",linewidth=2)
    plot(temps,couple_el,'b--',label = "Couple electrique (Nm)",linewidth=1.75)
    plot(temps,couple_th,'r--',label = "Couple thermique (Nm)",linewidth=1.75)
    plot(temps,efficacite2,'r',label = "Efficacite",linewidth=1.5)
    
    legend(loc="upper left",labelspacing = 0.5,prop={'size':25})
    grid()
    plt.ylabel('Vitesse et Efficacite',size=35)    
    plt.xlabel("Temps (s)",size=35)
    plt.title("Calcul de l'efficacite",size=45)
    show()
    
def main():
    repartition_gloutonne(NEDC,0,100,100,1000)


    
                #########################################
                #                                       #
                #        Fonctions elementaires         #
                #     Parcours, couple, regime, CSP     #
                #                                       #
                #########################################


#Nouveau cycle européen de conduite
def NEDC(t):
    if t<10:
        return 0
    if t<15:
        return 3*(t-10)
    if t<25:
        return 15
    if t<30:
        return 15 - 3*(t-25)
    if t< 50:
        return 0
    if t<60:
        return 3*(t-50)
    if t<85:
        return 30
    if t<95:
        return 30 - 3*(t-85)
    if t<120:
        return 0
    if t<145:
        return 2*(t-120)
    if t<155:
        return 50
    if t<163:
        return 50 - (t-155)*2.5
    if t<170:
        return 30
    if t<180:
        return 30 - (t-170)*3
    if t<210:
        return 0
    if t<215:
        return 3*(t-210)
    if t<225:
        return 15
    if t<230:
        return 15 - 3*(t-225)
    if t< 250:
        return 0
    if t<260:
        return 3*(t-250)
    if t<285:
        return 30
    if t<295:
        return 30 - 3*(t-285)
    if t<320:
        return 0
    if t<345:
        return 2*(t-320)
    if t<355:
        return 50
    if t<363:
        return 50 - (t-355)*2.5
    if t<370:
        return 30
    if t<380:
        return 30 - (t-370)*3
    if t<410:
        return 0
    if t<415:
        return 3*(t-410)
    if t<425:
        return 15
    if t<430:
        return 15 - 3*(t-425)
    if t< 450:
        return 0
    if t<460:
        return 3*(t-450)
    if t<485:
        return 30
    if t<495:
        return 30 - 3*(t-485)
    if t<520:
        return 0
    if t<545:
        return 2*(t-520)
    if t<555:
        return 50
    if t<563:
        return 50 - (t-555)*2.5
    if t<570:
        return 30
    if t<580:
        return 30 - (t-570)*3
    if t<610:
        return 0
    if t<615:
        return 3*(t-610)
    if t<625:
        return 15
    if t<630:
        return 15 - 3*(t-625)
    if t< 650:
        return 0
    if t<660:
        return 3*(t-650)
    if t<685:
        return 30
    if t<695:
        return 30 - 3*(t-685)
    if t<720:
        return 0
    if t<745:
        return 2*(t-720)
    if t<755:
        return 50
    if t<763:
        return 50 - (t-755)*2.5
    if t<770:
        return 30
    if t<780:
        return 30 - (t-770)*3
    if t<820:
        return 0
    if t<855:
        return (t-820)*2
    if t<910:
        return 70
    if t<920:
        return 70 - (t-910)*2
    if t<990:
        return 50
    if t<1000:
        return 50 + 2*(t-990)
    if t<1050:
        return 70
    if t<1080:
        return 70 + (t - 1050)
    if t<1110:
        return 100
    if t<1120:
        return 100 + 2*(t-1110)
    if t<1130:
        return 120
    if t<1160:
        return 120 - (t-1130)*4
    return 0

    
def trace_nedc():
    x = [i*0.05 for i in range(int(1200/0.05))]
    y = [NEDC(t) for t in x]
    plot(x,y,'b',label = "Vitesse du vehicule")
    legend()
    grid()
    plt.ylabel('Vitesse (km/h)')    
    plt.xlabel("Temps (s)")
    plt.title('Le Parcours NEDC')
    show()

# Renvoie l'angle de la pente en radians
def alpha(t):
    return 0

def acceleration(t):
    return (NEDC((t+0.01))-NEDC(t))/(0.01*3.6)
    
def rapport(t):
    vit = NEDC(t)
    if vit <= 20:
        return R1
    if vit <= 40:
        return R2
    if vit <= 60:
        return R3
    if vit <= 80:
        return R4
    return R5
 
       
#Calcul du couple à la roue à un instant t
def couple_roue(t):
    #Calclul des forces resistantes
    v = NEDC(t)
    f_aero = 0.5 * g_air * S_f * C_x * (v/3.6)**2
    if v != 0:
        f_roul = M_veh *  g * (a+b*((v/3.6)**2)) * cos(alpha(t))
    else:
        f_roul = 0
    f_grav = M_veh * g * sin(alpha(t))
    F_res = f_aero + f_roul + f_grav
    #Calcul de la force de traction nécessaire   
    acc = acceleration(t)
    F_trac = F_res + M_veh*acc
    return (F_trac * R_pneu)
 
#Calcul de la puissance instantanée necessaire pour avancer   
def puissance_inst(t): 
    F_trac = couple_roue(t)/R_pneu
    P = F_trac*NEDC(t)/3.6
    return P

#Calcul du couple à fournir par le moteur
def couple_moteur(t):
    return (couple_roue(t)/rapport(t))
    
def trace_couple():
    temps = [i*0.01 for i in range(int(1200/0.01))]
    couple = [couple_roue(t) for t in temps]
    vit = [NEDC(t) for t in temps]
    acc =[acceleration(t) for t in temps]
    plot(temps,couple,label = 'Couple')
    plot(temps,vit,label = 'Vitesse')
    plot(temps,acc,label = 'Acceleration')
    legend()
    grid()    
    show()
    
#Calcul du regime en tours/min
def regime(t):
    v = NEDC(t)/(3.6) #v en m/s
    rap = rapport(t)
    w_roue = v/R_pneu 
    w_mot = (w_roue * rap)*60/(2*pi) #en tours/min
    return w_mot

# Carte du rendement (il est equivalent d'utiliser la CSP par proportionnalite)
def rendement(couple,regime):    
    if couple>125 and couple<150 and (regime<2000 and regime>1600):
        return 0.35
    if couple>130 and couple<160 and regime>2200 and regime<2600:
        return 0.35
    if couple>115 and regime<2700 and regime>1300:
        return 0.33
    if couple>105 and regime<2400 and regime>1400:
        return 0.33
    if couple>95 and regime<2200 and regime>1500:
        return 0.33
    if couple>95 and regime<3100 and regime>1200:
        return 0.31
    if couple>85 and regime<2900 and regime>1300:
        return 0.31
    if couple>75 and regime<2500 and regime>1300:
        return 0.31
    if couple>65 and regime<2200 and regime>1600:
        return 0.31
    if couple>105 and couple<145 and regime<3200 and regime>1200:
        return 0.31
    if couple>110 and couple<135 and regime<3400 and regime>1200:
        return 0.31
    if couple>60 and regime>800 and regime<3400:
        return 0.29
    if couple>55 and regime>1000 and regime<2800:
        return 0.29
    if couple>50 and regime>1300 and regime<2200:
        return 0.29
    if couple>70 and couple<155 and regime>800 and regime<3600:
        return 0.29
    if couple>80 and couple<125 and regime>800 and regime<3800:
        return 0.29
    if couple>65 and regime>800:
        return 0.26
    if couple>55 and regime>700 and regime<4000:
        return 0.26
    if couple>45 and regime<3800 and regime>700:
        return 0.26
    if couple>40 and regime<3200 and regime>700:
        return 0.26
    if couple>35 and regime<2200 and regime>500:
        return 0.26
    if couple>30 and regime<1300 and regime>500:
        return 0.26
    if couple>35 and regime<4200 and regime>500:
        return 0.20
    if couple>25 and regime<3400 and regime>500:
        return 0.20
    if couple>15 and regime>1200 and regime>500:
        return 0.20
    return 0.15
   