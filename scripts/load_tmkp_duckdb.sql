PRAGMA threads=8;

DROP VIEW IF EXISTS edges_enriched;
DROP TABLE IF EXISTS edge_sources;
DROP TABLE IF EXISTS edge_publications;
DROP TABLE IF EXISTS node_equivalent_identifiers;
DROP TABLE IF EXISTS node_categories;
DROP TABLE IF EXISTS release_metadata;
DROP TABLE IF EXISTS graph_metadata;
DROP TABLE IF EXISTS edges;
DROP TABLE IF EXISTS nodes;
DROP TABLE IF EXISTS _edge_probe;

CREATE TABLE nodes AS
SELECT *
FROM read_json(
    'downloads/tmkp/2026_04_21/kgx/nodes.jsonl',
    format='newline_delimited',
    maximum_object_size=10485760,
    columns={
        id: 'VARCHAR',
        category: 'VARCHAR[]',
        name: 'VARCHAR',
        equivalent_identifiers: 'VARCHAR[]',
        information_content: 'DOUBLE',
        description: 'VARCHAR'
    }
);

CREATE TABLE edges AS
SELECT *
FROM read_json(
    'downloads/tmkp/2026_04_21/kgx/edges.jsonl',
    format='newline_delimited',
    maximum_object_size=10485760,
    columns={
        id: 'VARCHAR',
        category: 'VARCHAR[]',
        subject: 'VARCHAR',
        predicate: 'VARCHAR',
        object: 'VARCHAR',
        publications: 'VARCHAR[]',
        sources: 'JSON',
        knowledge_level: 'VARCHAR',
        agent_type: 'VARCHAR',
        has_supporting_studies: 'JSON',
        has_confidence_score: 'DOUBLE',
        evidence_count: 'BIGINT',
        object_aspect_qualifier: 'VARCHAR',
        object_direction_qualifier: 'VARCHAR',
        qualified_predicate: 'VARCHAR',
        subject_form_or_variant_qualifier: 'VARCHAR',
        original_subject: 'VARCHAR',
        original_object: 'VARCHAR',
        semmed_agreement_count: 'BIGINT'
    }
);

CREATE TABLE graph_metadata AS
SELECT *
FROM read_json_auto('downloads/tmkp/2026_04_21/graph-metadata.json');

CREATE TABLE release_metadata AS
SELECT *
FROM read_json_auto('downloads/tmkp/2026_04_21/latest-release.json');

CREATE TABLE node_categories AS
SELECT id AS node_id, unnest(category) AS category
FROM nodes;

CREATE TABLE node_equivalent_identifiers AS
SELECT id AS node_id, unnest(equivalent_identifiers) AS equivalent_identifier
FROM nodes;

CREATE TABLE edge_publications AS
SELECT id AS edge_id, unnest(publications) AS publication
FROM edges;

CREATE TABLE edge_sources AS
SELECT
    e.id AS edge_id,
    json_extract_string(source.value, '$.resource_id') AS resource_id,
    json_extract_string(source.value, '$.resource_role') AS resource_role,
    json_extract(source.value, '$.upstream_resource_ids') AS upstream_resource_ids
FROM edges AS e, json_each(e.sources) AS source;

CREATE VIEW edges_enriched AS
SELECT
    e.*,
    split_part(e.subject, ':', 1) AS subject_prefix,
    s.name AS subject_name,
    s.category[1] AS subject_primary_category,
    split_part(e.object, ':', 1) AS object_prefix,
    o.name AS object_name,
    o.category[1] AS object_primary_category,
    e.category[1] AS edge_primary_category
FROM edges AS e
LEFT JOIN nodes AS s ON s.id = e.subject
LEFT JOIN nodes AS o ON o.id = e.object;

CREATE INDEX nodes_id_idx ON nodes(id);
CREATE INDEX edges_id_idx ON edges(id);
CREATE INDEX edges_subject_idx ON edges(subject);
CREATE INDEX edges_object_idx ON edges(object);
CREATE INDEX edges_predicate_idx ON edges(predicate);
CREATE INDEX edges_spo_idx ON edges(subject, predicate, object);
CREATE INDEX edge_publications_publication_idx ON edge_publications(publication);
CREATE INDEX edge_sources_resource_role_idx ON edge_sources(resource_id, resource_role);

ANALYZE;
