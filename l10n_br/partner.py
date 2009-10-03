# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import osv, fields

##############################################################################
# Parceiro Personalizado
##############################################################################
class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'tipo_pessoa': fields.selection([('F', 'Física'), ('J', 'Jurídica')], 'Tipo de pessoa', required=True),
        'cnpj_cpf': fields.char('CNPJ/CPF', size=18),
        'inscr_est': fields.char('Inscr. Estadual', size=16),
    }

    _defaults = {
        'tipo_pessoa': lambda *a: 'J',
    }
        
    def _check_cnpj_cpf(self, cr, uid, ids):
        partner = self.browse(cr, uid, ids)[0]
        if not partner.cnpj_cpf:
            return True

        if partner.tipo_pessoa == 'J':
            return self.validate_cnpj(partner.cnpj_cpf)
        elif partner.tipo_pessoa == 'F':
            return self.validate_cpf(partner.cnpj_cpf)
        
        return False
    
    def validate_cnpj(self, cnpj):
        # Limpando o cnpj
        if not cnpj.isdigit():
            import re
            cnpj = re.sub('[^0-9]', '', cnpj)
           
        # verificando o tamano do  cnpj
        if len(cnpj) != 14:
            return False
            
        # Pega apenas os 12 primeiros dígitos do CNPJ e gera os 2 dígitos que faltam
        cnpj= map(int, cnpj)
        novo = cnpj[:12]

        prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        while len(novo) < 14:
            r = sum([x*y for (x, y) in zip(novo, prod)]) % 11
            if r > 1:
                f = 11 - r
            else:
                f = 0
            novo.append(f)
            prod.insert(0, 6)

        # Se o número gerado coincidir com o número original, é válido
        if novo == cnpj:
            return True
            
        return False
    
    def validate_cpf(self, cpf):           
        if not cpf.isdigit():
            import re
            cpf = re.sub('[^0-9]', '', cpf)

        if len(cpf) != 11:
            return False

        # Pega apenas os 9 primeiros dígitos do CPF e gera os 2 dígitos que faltam
        cpf = map(int, cpf)
        novo = cpf[:9]

        while len(novo) < 11:
            r = sum([(len(novo)+1-i)*v for i,v in enumerate(novo)]) % 11

            if r > 1:
                f = 11 - r
            else:
                f = 0
            novo.append(f)

        # Se o número gerado coincidir com o número original, é válido
        if novo == cpf:
            return True
            
        return False

    _constraints = [(_check_cnpj_cpf, 'CNPJ/CPF invalido!', ['cnpj_cpf'])]

    def _on_change_mask_cnpj_cpf(self, cr, uid, ids, tipo_pessoa, cnpj_cpf):
        if not cnpj_cpf or not tipo_pessoa:
            return {}

        import re
        val = re.sub('[^0-9]', '', cnpj_cpf)

        if tipo_pessoa == 'J' and len(val) == 14:            
            cnpj_cpf = "%s.%s.%s/%s-%s" % (val[0:2], val[2:5], val[5:8], val[8:12], val[12:14])
        
        elif tipo_pessoa == 'F' and len(val) == 11:
            cnpj_cpf = "%s.%s.%s-%s" % (val[0:3], val[3:6], val[6:9], val[9:11])
        
        return {'value': {'tipo_pessoa': tipo_pessoa, 'cnpj_cpf': cnpj_cpf}}
    
    def zip_search(self, cr, uid, ids, context={}):
        return True
    
res_partner()

##############################################################################
# Contato do Parceiro Personalizado
##############################################################################
class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    _columns = {
	'city_id': fields.many2one('l10n_br.city', 'Municipio'),
        'number': fields.char('Número', size=10),
    }

res_partner_address()