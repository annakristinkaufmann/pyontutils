#!/usr/bin/env python3.6
""" Various ontology refactors. Run in the root ttl folder.

Usage:
    ontload uri-switch [options]
    ontload backend-refactor [options] <file>...
    ontload todo [options] <repo>

Options:
    -l --git-local=LBASE            local path to look for ontology <repo> [default: /tmp]

    -u --curies=CURIEFILE           relative path to curie definition file [default: ../scigraph/nifstd_curie_map.yaml]

    -d --debug                      call IPython embed when done
"""
import os
from glob import glob
import rdflib
from joblib import Parallel, delayed
from pyontutils.utils import makePrefixes, makeGraph, createOntology, noneMembers, anyMembers, owl
from pyontutils.ontload import loadall, locate_config_file, getCuries
from IPython import embed

# common

def do_file(filename, swap, *args):
    print('START', filename)
    ng = rdflib.Graph()
    ng.parse(filename, format='turtle')
    reps = switchURIs(ng, swap, *args)
    wg = makeGraph('', graph=ng)
    wg.filename = filename
    wg.write()
    print('END', filename)
    return reps

def switchURIs(g, swap, *args):
    reps = []
    prefs = {None}
    addpg = makeGraph('', graph=g)
    for t in g:
        nt, ireps, iprefs = tuple(zip(*swap(t, *args)))
        if t != nt:
            g.remove(t)
            g.add(nt)

        for rep in ireps:
            if rep is not None:
                reps.append(rep)

        for pref in iprefs:
            if pref not in prefs:
                prefs.add(pref)
                addpg.add_known_namespaces(fragment_prefixes[pref])
    return reps

#
# uri switch

def uri_switch_values(utility_graph):
    NIFSTDBASE = 'http://uri.neuinfo.org/nif/nifstd/'

    fragment_prefixes = {
        'NIFRID':'NIFRID',
        'NIFSTD':'NIFSTD',  # no known collisions, mostly for handling ureps
        'birnlex_':'BIRNLEX',
        'sao':'SAO',
        'sao-':'FIXME_SAO',  # FIXME
        'nif_organ_':'FIXME_NIFORGAN',  # single and seems like a mistake for nlx_organ_
        'nifext_':'NIFEXT',
        #'nifext_5007_',  # not a prefix
        'nlx_':'NLX',
        #'nlx_0906_MP_',  # not a prefix, sourced from mamalian phenotype ontology and prefixed TODO
        #'nlx_200905_',  # not a prefix
        'nlx_anat_':'NLXANAT',
        'nlx_cell_':'NLXCELL',
        'nlx_chem_':'NLXCHEM',
        'nlx_dys_':'NLXDYS',
        'nlx_func_':'NLXFUNC',
        'nlx_inv_':'NLXINV',
        'nlx_mol_':'NLXMOL',
        'nlx_neuron_nt_':'NLXNEURNT',
        'nlx_organ_':'NLXORG',
        'nlx_qual_':'NLXQUAL',
        'nlx_res_':'NLXRES',
        'nlx_sub_':'FIXME_NLXSUBCELL',  # FIXME one off mistake for nlx_subcell?
        'nlx_subcell_':'NLXSUB',   # NLXSUB??
        'nlx_ubo_':'NLXUBO',
        'nlx_uncl_':'NLXUNCL',
    }

    uri_replacements = {
        # Classes
        'NIFCELL:Class_6':'NIFSTD:Class_6',
        'NIFCHEM:CHEBI_18248':'NIFSTD:CHEBI_18248',
        'NIFCHEM:CHEBI_26020':'NIFSTD:CHEBI_26020',
        'NIFCHEM:CHEBI_27958':'NIFSTD:CHEBI_27958',
        'NIFCHEM:CHEBI_35469':'NIFSTD:CHEBI_35469',
        'NIFCHEM:CHEBI_35476':'NIFSTD:CHEBI_35476',
        'NIFCHEM:CHEBI_3611':'NIFSTD:CHEBI_3611',
        'NIFCHEM:CHEBI_49575':'NIFSTD:CHEBI_49575',
        'NIFCHEM:DB00813':'NIFSTD:DB00813',
        'NIFCHEM:DB01221':'NIFSTD:DB01221',
        'NIFCHEM:DB01544':'NIFSTD:DB01544',
        'NIFGA:Class_12':'NIFSTD:Class_12',
        'NIFGA:Class_2':'NIFSTD:Class_2',  # FIXME this record is not in neurolex
        'NIFGA:Class_4':'NIFSTD:Class_4',
        'NIFGA:FMAID_7191':'NIFSTD:FMA_7191',  # FIXME http://neurolex.org/wiki/FMA:7191
        'NIFGA:UBERON_0000349':'NIFSTD:UBERON_0000349',
        'NIFGA:UBERON_0001833':'NIFSTD:UBERON_0001833',
        'NIFGA:UBERON_0001886':'NIFSTD:UBERON_0001886',
        'NIFGA:UBERON_0002102':'NIFSTD:UBERON_0002102',
        'NIFINV:OBI_0000470':'NIFSTD:OBI_0000470',
        'NIFINV:OBI_0000690':'NIFSTD:OBI_0000690',
        'NIFINV:OBI_0000716':'NIFSTD:OBI_0000716',
        'NIFMOL:137140':'NIFSTD:137140',
        'NIFMOL:137160':'NIFSTD:137160',
        'NIFMOL:D002394':'NIFSTD:D002394',
        'NIFMOL:D008995':'NIFSTD:D008995',
        'NIFMOL:DB00668':'NIFSTD:DB00668',
        'NIFMOL:GO_0043256':'NIFSTD:GO_0043256',  # FIXME http://neurolex.org/wiki/GO:0043256
        'NIFMOL:IMR_0000512':'NIFSTD:IMR_0000512',
        'NIFRES:Class_2':'NLX:293',  # FIXME note that neurolex still thinks Class_2 goes here... not to NIFGA:Class_2
        'NIFSUB:FMA_83604':'NIFSTD:FMA_83604',  # FIXME http://neurolex.org/wiki/FMA:83604
        'NIFSUB:FMA_83605':'NIFSTD:FMA_83605',  # FIXME http://neurolex.org/wiki/FMA:83605
        'NIFSUB:FMA_83606':'NIFSTD:FMA_83606',  # FIXME http://neurolex.org/wiki/FMA:83606
        'NIFUNCL:CHEBI_24848':'NIFSTD:CHEBI_24848',  # FIXME not in interlex and not in neurolex_full.csv but in neurolex (joy)
        'NIFUNCL:GO_0006954':'NIFSTD:GO_0006954',  # FIXME http://neurolex.org/wiki/GO:0006954
    }
    uri_reps_nonstandard = {
        # nonstandards XXX none of these collide with any other namespace
        # that we might like to use in the future under NIFSTD:namespace/
        # therefore they are being placed directly into NIFSTD and we will
        # work out the details and redirects later (some intlerlex classes
        # may need to be created) maybe when we do the backend refactor.

        # Classes (from backend)
        'BIRNANN:_birnlex_limbo_class':'NIFRID:birnlexLimboClass',
        'BIRNANN:_birnlex_retired_class':'NIFRID:birnlexRetiredClass',
        rdflib.URIRef('http://ontology.neuinfo.org/NIF/Backend/DC_Term'):'NIFRID:dctermsClass',
        rdflib.URIRef('http://ontology.neuinfo.org/NIF/Backend/SKOS_Entity'):'NIFRID:skosClass',
        rdflib.URIRef('http://ontology.neuinfo.org/NIF/Backend/_backend_class'):'NIFRID:BackendClass',
        rdflib.URIRef('http://ontology.neuinfo.org/NIF/Backend/oboInOwlClass'):'NIFRID:oboInOwlClass',

        # NamedIndividuals
        'NIFORG:Infraclass':'NIFRID:Infraclass',  # only used in annotaiton but all other similar cases show up as named individuals
        'NIFORG:first_trimester':'NIFRID:first_trimester',
        'NIFORG:second_trimester':'NIFRID:second_trimester',
        'NIFORG:third_trimester':'NIFRID:third_trimester',

        # ObjectProperties not in OBOANN or BIRNANN
        'NIFGA:has_lacking_of':'NIFRID:has_lacking_of',
        'NIFNEURNT:has_molecular_constituent':'NIFRID:has_molecular_constituent',
        'NIFNEURNT:has_neurotransmitter':'NIFRID:has_neurotransmitter',
        'NIFNEURNT:molecular_constituent_of':'NIFRID:molecular_constituent_of',
        'NIFNEURNT:neurotransmitter_of':'NIFRID:neurotransmitter_of',
        'NIFNEURNT:soma_located_in':'NIFRID:soma_located_in',
        'NIFNEURNT:soma_location_of':'NIFRID:soma_location_of',

        # AnnotationProperties not in OBOANN or BIRNANN
        'NIFCHEM:hasStreetName':'NIFRID:hasStreetName',
        'NIFMOL:hasGenbankAccessionNumber':'NIFRID:hasGenbankAccessionNumber',
        'NIFMOL:hasLocusMapPosition':'NIFRID:hasLocusMapPosition',
        'NIFMOL:hasSequence':'NIFRID:hasSequence',
        'NIFORG:hasCoveringOrganism':'NIFRID:hasCoveringOrganism',
        'NIFORG:hasMutationType':'NIFRID:hasMutationType',
        'NIFORG:hasTaxonRank':'NIFRID:hasTaxonRank',
    }

    utility_graph.add_known_namespaces(*(c for c in fragment_prefixes.values() if 'FIXME' not in c))
    ureps = {utility_graph.expand(k):utility_graph.expand(v)
                        for k, v in uri_replacements.items()}
    ureps.update({utility_graph.check_thing(k):utility_graph.expand(v)
                  for k, v in uri_reps_nonstandard.items()})

    return fragment_prefixes, ureps

def uri_switch(filenames, get_values):
    replacement_graph = createOntology('NIF-NIFSTD-mapping',
                                       'NIF* to NIFSTD equivalents',
                                       makePrefixes(
                                           'BIRNANN', 'BIRNOBI', 'BIRNOBO', 'NIFANN',
                                           'NIFCELL', 'NIFCHEM', 'NIFDYS', 'NIFFUN',
                                           'NIFGA', 'NIFGG', 'NIFINV', 'NIFMOL',
                                           'NIFMOLINF', 'NIFMOLROLE', 'NIFNCBISLIM',
                                           'NIFNEURBR', 'NIFNEURBR2', 'NIFNEURCIR',
                                           'NIFNEURMC', 'NIFNEURMOR', 'NIFNEURNT',
                                           'NIFORG', 'NIFQUAL', 'NIFRES', 'NIFRET',
                                           'NIFSCID', 'NIFSUB', 'NIFUNCL', 'OBOANN',
                                           'SAOCORE')
                                      )
    fragment_prefixes, ureps = get_values(replacement_graph)
    print('Start writing')
    trips_lists = Parallel(n_jobs=9)(delayed(do_file)(f, swapUriSwitch, ureps, fragment_prefixes) for f in filenames)
    print('Done writing')
    [replacement_graph.g.add(t) for trips in trips_lists for t in trips]
    replacement_graph.write()

def swapUriSwitch(trip, ureps, fragment_prefixes):
    for spo in trip:
        if not isinstance(spo, rdflib.URIRef):
            yield spo, None, None
            continue
        elif spo in ureps:
            new_spo = ureps[spo]
            rep = (new_spo, owl.sameAs, spo)
            if 'nlx_' in new_spo:
                pref = 'nlx_'
            elif '/readable/' in new_spo:
                pref = 'NIFRID'
            else:
                pref = 'NIFSTD'
            yield new_spo, rep, pref
            continue
        elif anyMembers(spo,  # backend refactor
                        'BIRNLex_annotation_properties.owl#',
                        'OBO_annotation_properties.owl#'):
            _, suffix = spo.rsplit('#', 1)
            new_spo = rdflib.URIRef(os.path.join(NIFSTDBASE, 'readable', suffix))
            rep = (new_spo, owl.sameAs, spo)
            pref = 'NIFRID'
            yield new_spo, rep, pref
            continue

        try:
            uri_pref, fragment = spo.rsplit('#', 1)
            if '_' in fragment:
                frag_pref, p_suffix = fragment.split('_', 1)
                if not p_suffix[0].isdigit():
                    p, suffix = p_suffix.split('_', 1)
                    frag_pref = frag_pref + '_' + p
                else:
                    suffix = p_suffix
                frag_pref_ = frag_pref + '_'
                if frag_pref_ in fragment_prefixes:
                    if frag_pref_ == 'nlx_sub_': pref = 'nlx_subcell_'
                    elif frag_pref_ == 'nif_organ_': pref = 'nlx_organ_'
                    else: pref = frag_pref_  # come on branch predictor you can do it!
                elif frag_pref_ == 'nlx_neuron_':  # special case
                    rest = 'nt_'
                    suffix = suffix[len(rest):]
                    pref = frag_pref_ + rest
                else:
                    yield spo, None, None
                    continue
            elif 'sao' in fragment:
                suffix = fragment[3:].strip('-')
                pref = 'sao'
            else:
                yield spo, None, None
                continue
            new_spo = rdflib.URIRef(NIFSTDBASE + pref + suffix)
            if new_spo != spo:
                rep = (new_spo, owl.sameAs, spo)
            else:
                rep = None
                print('Already converted', spo)
            yield new_spo, rep, pref
        except ValueError:  # there was no # so do not split
            yield spo, None, None
            continue

#
# backend

def backend_refactor_values():
    uri_reps_lit = {
        # from https://github.com/information-artifact-ontology/IAO/blob/master/docs/BFO%201.1%20to%202.0%20conversion/mapping.txt
        'http://www.ifomis.org/bfo/1.1#Entity':'BFO:0000001',
        'BFO1SNAP:Continuant':'BFO:0000002',
        'BFO1SNAP:Disposition':'BFO:0000016',
        'BFO1SNAP:Function':'BFO:0000034',
        'BFO1SNAP:GenericallyDependentContinuant':'BFO:0000031',
        'BFO1SNAP:IndependentContinuant':'BFO:0000004',
        'BFO1SNAP:MaterialEntity':'BFO:0000040',
        'BFO1SNAP:Quality':'BFO:0000019',
        'BFO1SNAP:RealizableEntity':'BFO:0000017',
        'BFO1SNAP:Role':'BFO:0000023',
        'BFO1SNAP:Site':'BFO:0000029',
        'BFO1SNAP:SpecificallyDependentContinuant':'BFO:0000020',
        'BFO1SPAN:Occurrent':'BFO:0000003',
        'BFO1SPAN:ProcessualEntity':'BFO:0000015',
        'BFO1SPAN:Process':'BFO:0000015',
        'BFO1SNAP:ZeroDimensionalRegion':'BFO:0000018',
        'BFO1SNAP:OneDimensionalRegion':'BFO:0000026',
        'BFO1SNAP:TwoDimensionalRegion':'BFO:0000009',
        'BFO1SNAP:ThreeDimensionalRegion':'BFO:0000028',
        'http://purl.org/obo/owl/OBO_REL#bearer_of':'RO:0000053',
        'http://purl.org/obo/owl/OBO_REL#inheres_in':'RO:0000052',
        'ro:has_part':'BFO:0000051',
        'ro:part_of':'BFO:0000050',
        'ro:has_participant':'RO:0000057',
        'ro:participates_in':'RO:0000056',
        'http://purl.obolibrary.org/obo/OBI_0000294':'RO:0000059',
        'http://purl.obolibrary.org/obo/OBI_0000297':'RO:0000058',
        'http://purl.obolibrary.org/obo/OBI_0000300':'BFO:0000054',
        'http://purl.obolibrary.org/obo/OBI_0000308':'BFO:0000055',

        # more bfo
        'BFO1SNAP:SpatialRegion':'BFO:0000006',
        'BFO1SNAP:FiatObjectPart':'BFO:0000024',
        'BFO1SNAP:ObjectAggregate':'BFO:0000027',
        'BFO1SNAP:Object':'BFO:0000030',
        #'BFO1SNAP:ObjectBoundary'  # no direct replacement, only occurs in unused
        #'BFO1SPAN:ProcessAggregate'  # was not replaced, could simply be a process itself??
        #'BFO1SNAP:DependentContinuant'  # was not replaced

        # other
        #'ro:participates_in'  # above
        #'ro:has_participant'  # above
        #'ro:has_part',  # above
        #'ro:part_of',  # above
        #'ro:precedes'  # unused and only in inferred
        #'ro:preceded_by'  # unused and only in inferred
        #'ro:transformation_of'  # unused and only in inferred
        #'ro:transformed_into'  # unused and only in inferred

        'http://purl.org/obo/owl/obo#inheres_in':'RO:0000052',
        'http://purl.obolibrary.org/obo/obo#towards':'RO:0002503',
        'http://purl.org/obo/owl/pato#towards':'RO:0002503',

        'http://purl.obolibrary.org/obo/pato#inheres_in':'RO:0000052',
        'BIRNLEX:17':'RO:0000053',  # is_bearer_of
        'http://purl.obolibrary.org/obo/pato#towards':'RO:0002503',
        'ro:adjacent_to':'RO:0002220',

        'ro:derives_from':'RO:0001000',
        'ro:derives_into':'RO:0001001',

        'ro:agent_in':'RO:0002217',
        'ro:has_agent':'RO:0002218',

        'ro:contained_in':'RO:0001018',
        'ro:contains':'RO:0001019',

        'ro:located_in':'RO:0001025',
        'ro:location_of':'RO:0001015',

        'ro:has_proper_part':'NIFRID:has_proper_part',
        'ro:proper_part_of':'NIFRID:proper_part_of',  # part of where things are not part of themsevles need to review
    }
    ug = makeGraph('', prefixes=makePrefixes('ro', 'RO', 'BIRNLEX', 'NIFRID',
                                             'BFO', 'BFO1SNAP', 'BFO1SPAN'))
    ureps = {ug.check_thing(k):ug.check_thing(v)
             for k, v in uri_reps_lit.items()}

    return ureps

def swapBackend(trip, ureps):
    for spo in trip:
        if spo in ureps:
            new_spo = ureps[spo]
            rep = (new_spo, owl.sameAs, spo)
            yield new_spo, rep, None
        else:
            yield spo, None, None

def backend_refactor(filenames, get_values):
    ureps = get_values()
    print('Start writing')
    trips_lists = Parallel(n_jobs=9)(delayed(do_file)(f, swapBackend, ureps) for f in filenames)
    print('Done writing')
    embed()

#
# graph todo

def graph_todo(graph, curie_prefixes, get_values):
    ug = makeGraph('big-graph', graph=graph)
    ug.add_known_namespaces('NIFRID')
    fragment_prefixes, ureps = get_values(ug)
    #all_uris = sorted(set(_ for t in graph for _ in t if type(_) == rdflib.URIRef))  # this snags a bunch of other URIs
    #all_uris = sorted(set(_ for _ in graph.subjects() if type(_) != rdflib.BNode))
    #all_uris = set(spo for t in graph.subject_predicates() for spo in t if isinstance(spo, rdflib.URIRef))
    all_uris = set(spo for t in graph for spo in t if isinstance(spo, rdflib.URIRef))
    prefs = set(_.rsplit('#', 1)[0] + '#' if '#' in _
                       else (_.rsplit('_',1)[0] + '_' if '_' in _
                             else _.rsplit('/',1)[0] + '/') for _ in all_uris)
    nots = set(_ for _ in prefs if _ not in curie_prefixes)  # TODO
    sos = set(prefs) - set(nots)
    all_uris = [u if u not in ureps
                else ureps[u]
                for u in all_uris]
    #to_rep = set(_.rsplit('#', 1)[-1].split('_', 1)[0] for _ in all_uris if 'ontology.neuinfo.org' in _)
    #to_rep = set(_.rsplit('#', 1)[-1] for _ in all_uris if 'ontology.neuinfo.org' in _)

    ignore = (
        # deprecated and only in as annotations
        'NIFGA:birnAnatomy_011',
        'NIFGA:birnAnatomy_249',
        'NIFORG:birnOrganismTaxon_19',
        'NIFORG:birnOrganismTaxon_20',
        'NIFORG:birnOrganismTaxon_21',
        'NIFORG:birnOrganismTaxon_390',
        'NIFORG:birnOrganismTaxon_391',
        'NIFORG:birnOrganismTaxon_56',
        'NIFORG:birnOrganismTaxon_68',
        'NIFINV:birnlexInvestigation_174',
        'NIFINV:birnlexInvestigation_199',
        'NIFINV:birnlexInvestigation_202',
        'NIFINV:birnlexInvestigation_204',
    )
    ignore = tuple(ug.expand(i) for i in ignore)


    non_normal_identifiers = sorted(u for u in all_uris
                                    if 'ontology.neuinfo.org' in u
                                    and noneMembers(u, *fragment_prefixes)
                                    and not u.endswith('.ttl')
                                    and not u.endswith('.owl')
                                    and u not in ignore)
    print(len(prefs))
    embed()

def main():
    from docopt import docopt
    args = docopt(__doc__, version='refactor 0')

    repo_name = args['<repo>']

    git_local = args['--git-local']

    curies_location = args['--curies']
    curies_location = locate_config_file(curies_location, git_local)
    curies, curie_prefixes = getCuries(curies_location)

    filenames = args['<file>']
    filenames.sort(key=lambda f: os.path.getsize(f), reverse=True)  # make sure the big boys go first
    for n in ('nif.ttl', 'resources.ttl', 'generated/chebislim.ttl', 'unused/ro_bfo_bridge.ttl',
              'generated/ncbigeneslim.ttl', 'generated/NIF-NIFSTD-mapping.ttl'):
        if n in filenames:
            filenames.remove(n)

    if args['uri-switch']:
        uri_switch(filenames, uri_switch_values)
    elif args['backend-refactor']:
        backend_refactor(filenames, backend_refactor_values)
    elif args['todo']:
        graph = loadall(git_local, repo_name, local=True)
        graph_todo(graph, curie_prefixes, uri_switch_values)
        embed()

if __name__ == '__main__':
    main()
