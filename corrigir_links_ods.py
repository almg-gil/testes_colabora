# -*- coding: utf-8 -*-
"""Corrige hyperlinks incorporados aos estilos da aba diaria em planilhas ODS.

A planilha MODELO da ALMG armazena links dos diarios em estilos de celula
(style:table-cell-properties/style:hyperlink), nao somente em formulas.
Ao copiar a aba, o LibreOffice mantem o link historico do MODELO.
Esta rotina clona os estilos usados somente na nova aba, preservando os
estilos das abas anteriores, e troca o destino para a data selecionada.
"""
from copy import deepcopy
from io import BytesIO
from zipfile import ZipFile
from lxml import etree

NS_T = 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'
NS_S = 'urn:oasis:names:tc:opendocument:xmlns:style:1.0'
NS_X = 'http://www.w3.org/1999/xlink'
NS_O = 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'


def corrigir_links_aba(ods: bytes, aba: str, urls: dict) -> bytes:
    """Atualiza apenas estilos com link de jornal da aba `aba`.

    `urls`: dicionario gerado por montar_urls() no extrator original.
    Na versao de teste o Diario Administrativo nao e consultado; seu link
    herdado do MODELO e removido para nao apontar para 20/02/2026.
    """
    entrada = BytesIO(ods)
    with ZipFile(entrada) as z:
        raiz = etree.fromstring(z.read('content.xml'))
        auto = raiz.find('.//{%s}automatic-styles' % NS_O)
        if auto is None:
            raise ValueError('Estilos automaticos nao encontrados no ODS')
        folhas = raiz.xpath('.//t:table[@t:name=$nome]', namespaces={'t': NS_T}, nome=aba)
        if len(folhas) != 1:
            raise ValueError('Aba %s nao encontrada (ou duplicada)' % aba)
        folha = folhas[0]
        estilos = {
            el.get('{%s}name' % NS_S): el
            for el in raiz.xpath('.//s:style[@s:family="table-cell"]', namespaces={'s': NS_S})
        }
        atuais = set(estilos)
        mapa = {}
        alteradas = 0
        for cel in folha.iter():
            if cel.tag != '{%s}table-cell' % NS_T:
                continue
            antigo = cel.get('{%s}style-name' % NS_T)
            if not antigo or antigo not in estilos:
                continue
            estilo = estilos[antigo]
            links = estilo.xpath('./s:table-cell-properties/s:hyperlink', namespaces={'s': NS_S})
            if not links:
                continue
            href = links[0].get('{%s}href' % NS_X, '')
            if 'jornalminasgerais.mg.gov.br' in href:
                novo_href = urls['executivo_html']
            elif 'diariolegislativo.almg.gov.br' in href:
                novo_href = urls['legislativo']
            elif 'intra.almg.gov.br' in href and 'diario-administrativo' in href:
                novo_href = None  # fonte desativada neste teste
            else:
                continue
            chave = (antigo, novo_href)
            if chave not in mapa:
                novo = deepcopy(estilo)
                i = 1
                nome = 'almg_%s_link_%d' % (aba, i)
                while nome in atuais:
                    i += 1
                    nome = 'almg_%s_link_%d' % (aba, i)
                atuais.add(nome)
                novo.set('{%s}name' % NS_S, nome)
                hiper = novo.xpath('./s:table-cell-properties/s:hyperlink', namespaces={'s': NS_S})
                for link in hiper:
                    if novo_href:
                        link.set('{%s}href' % NS_X, novo_href)
                    else:
                        link.getparent().remove(link)
                auto.append(novo)
                mapa[chave] = nome
            cel.set('{%s}style-name' % NS_T, mapa[chave])
            alteradas += 1
        if not alteradas:
            raise ValueError('Nenhum estilo com hyperlink de jornal na nova aba: conferir MODELO')
        xml = etree.tostring(raiz, encoding='UTF-8', xml_declaration=True)
        destino = BytesIO()
        with ZipFile(destino, 'w') as out:
            for info in z.infolist():
                out.writestr(info, xml if info.filename == 'content.xml' else z.read(info.filename))
    return destino.getvalue()
