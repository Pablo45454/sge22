# -*- coding: utf-8 -*-
import math

from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class player(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Players of the game'
    #name = fields.Char(required=True)
    password = fields.Integer()
    nivel = fields.Integer(default=1)
    hp = fields.Integer(compute="_get_hp")
    fuerza = fields.Integer(compute="_get_fuerza")
    destreza = fields.Integer(compute="_get_destreza")
    avatar = fields.Image(max_width=200,max_height=360)
    is_player = fields.Boolean(default=False)
    def _first_weapon(self):
        return self.env['warrior.arma'].search([])[0]
    arma = fields.Many2many("warrior.arma",default=_first_weapon,readonly="True")
    clase = fields.Many2one("warrior.clase")
    def _first_zone(self):
        return self.env['warrior.zona'].search([])[1]
    zona = fields.Many2one("warrior.zona",default=_first_zone)
    xp = fields.Integer(default=0)
    armadura = fields.Integer(related="clase.armadura")
    xp_required = fields.Integer(default=200,compute="_get_xp_required")
    avatar_clase = fields.Image(max_width=200, max_height=200, related="clase.avatar")
    avatar_zona = fields.Image(max_width=200, max_height=160, related="zona.avatar")
    name_zona = fields.Char(related="zona.name")
    dificultad_zona = fields.Selection(related="zona.dificultad")
    fecha = fields.Date(default=datetime.now(),readonly="True")
    tienda = fields.Many2one("warrior.arma")
    arma_avatar = fields.Image(max_width=80, max_height=80, related="tienda.avatar")
    arma_nombre = fields.Char(related="tienda.name")
    arma_precio = fields.Integer(related="tienda.precio")
    arma_damage = fields.Integer(related="tienda.damage")
    arma_afinidad = fields.Selection(related="tienda.afinidad")
    buy_available = fields.Char(readonly="True")

    @api.onchange('tienda')
    def _onchange_shop(self):
        if(self.xp<self.tienda.precio):
            self.write({'buy_available': "No tiene suficiente xp"})
        else: 
            self.write({'buy_available': "Se puede relizar la compra"})

    def comprar_arma(self):
        for s in self:
            if(s.xp>s.tienda.precio):
                self.write({'arma':[(4,s.tienda.id)]})
                nueva_xp = s.xp-s.tienda.precio
                s.write({'xp': nueva_xp})
    
    def aumentar_nivel(self):
        for s in self:

            lvl = (s.nivel+1)

            s.write({'nivel':lvl})

    def disminuir_nivel(self):
        for s in self:

            lvl = (s.nivel-1)

            s.write({'nivel':lvl})

    @api.constrains('nivel')
    def _min_lvl_exceeded(self):
        for s in self:
            if s.nivel < 1:
                raise ValidationError("Has excedido el nivel minimo: %s " % s.nivel+1)

    @api.constrains('nivel')
    def _max_lvl_exceeded(self):
        for s in self:
            if s.nivel > 99:
                raise ValidationError("Has excedido el nivel maximo: %s " % s.nivel-1)

    @api.depends('nivel')
    def _get_xp_required(self):
        for s in self:
            self.xp_required = 200*math.pow(1+(0.075),self.nivel-1)

    @api.depends('nivel')
    def _get_hp(self):
        for player in self:

            self.hp = self.clase.hp+(10*(player.nivel-1))

    @api.depends('nivel')
    def _get_fuerza(self):
        for player in self:
            self.fuerza = self.clase.fuerza+(1*(player.nivel-1))

    @api.depends('nivel')
    def _get_destreza(self):
        for player in self:
            self.destreza = self.clase.destreza+(1*(player.nivel-1))

    @api.model
    def give_xp(self):
        players = self.env['res.partner'].search([])
        for player in players:
            player.xp = player.xp+100


class clase(models.Model):
    _name = 'warrior.clase'
    _description = 'Players'
    name = fields.Char(required=True)
    hp = fields.Integer()
    fuerza = fields.Integer()
    destreza = fields.Integer()
    armadura = fields.Integer()
    avatar = fields.Image(max_width=200, max_height=200)
    

class zona(models.Model):
    _name = 'warrior.zona'
    _description = 'Zonas'
    name = fields.Char(required=True)
    avatar = fields.Image(max_width=300, max_height=300)
    dificultad = fields.Selection([('1','Neutral'),('2','Facil'),('3','Intermedio'),('4','Dificil'),('5','Experto')])
    mob = fields.One2many("warrior.mob","zona")
    player = fields.One2many("res.partner","zona")



class mob(models.Model):
    _name = 'warrior.mob'
    _description = 'Enemigos'
    name = fields.Char(required=True)
    zona = fields.Many2one("warrior.zona")
    hp = fields.Integer()
    damage = fields.Integer()
    avatar = fields.Image(max_width=200, max_height=200)
    mob_type = fields.Many2one("warrior.mob_type")

class mob_type(models.Model):
    _name = 'warrior.mob_type'
    _description = 'Tipo enemigo'
    name = fields.Char(required=True)
    mob = fields.One2many("warrior.mob","mob_type")


class arma(models.Model):
    _name = 'warrior.arma'
    _description = 'Arma'
    damage = fields.Integer()
    name = fields.Char(required=True)
    avatar = fields.Image(max_width=100, max_height=100)
    afinidad = fields.Selection([('1','Fuerza'),('2','Destreza'),('3','Ambos')])
    precio = fields.Integer()

class travel(models.Model):
    _name = 'warrior.travel'
    _description = 'Travel'
    players = fields.Many2one("res.partner")
    zona_destino = fields.Many2one("warrior.zona")
    zona_origen = fields.Many2one("warrior.zona",compute="_get_zona_origen",readonly="True")

    def batalla(self):
        for s in self:
            if(s.player.hp>s.mob.hp):
                s.write({'ganador': "Gana el jugador"})
                print("Ha ganado el player")
            else:
                print("Ha ganado el mob")
                s.write({'ganador': "Gana el mob"})


    @api.depends('players')
    def _get_zona_origen(self):
        for s in self:
            s.zona_origen = s.players.zona.id

    @api.constrains('zona_destino')
    def _same_zone(self):
        for s in self:
            if s.zona_origen.id == s.zona_destino.id:
                raise ValidationError('Ya se encuentra en la zona')

    def iniciar_viaje(self):
        for s in self:
            for p in s.players:
                p.write({'zona': s.zona_destino.id})



class battle_player(models.Model):
    _name = 'warrior.battle_player'
    _description = 'Batallas Jugadores'
    player1 = fields.Many2one("res.partner",ondelete="cascade")
    player2 = fields.Many2one("res.partner",ondelete="cascade")
    arma1 = fields.Many2one("warrior.arma")
    arma2 = fields.Many2one("warrior.arma")