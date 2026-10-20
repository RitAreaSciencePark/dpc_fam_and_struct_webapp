-- SYNTHETIC TEACHING DATA. These protein IDs, sequences, cluster statistics,
-- and Pfam assignments are invented, not research observations.
-- No exercise endpoints or their implementations are included here.
\set ON_ERROR_STOP on
BEGIN;

CREATE TABLE workshop_dataset_info (
    version integer PRIMARY KEY,
    description text NOT NULL
);
INSERT INTO workshop_dataset_info VALUES (1, 'Synthetic DPCexplorer API workshop dataset');

INSERT INTO dpc_uniprot_proteins (protein_id, protein_length)
SELECT 'WS' || lpad(n::text, 6, '0'), 600 FROM generate_series(1, 1000) AS n;
INSERT INTO dpc_uniprot_proteins VALUES
    ('WSDEMO0001', 600), ('WSEMPTY0001', 600),
    ('WSFAMONLY', 600), ('WSSTRUCTONLY', 600), ('WSPFAMONLY', 600);

INSERT INTO dpc_pfam_domains VALUES
    ('PF00001', 'Family'), ('PF00002', 'Family'), ('PF00003', 'Family');

INSERT INTO dpcfam_mcs_properties
    (mcid, size_uniref50, avg_len, std_avg_len, lc_percent, cc_percent,
     dis_percent, tm, pfam_da, da_percent, avg_ov_percent, overlap_label)
SELECT 'MC' || n, 0, 80, 0, 2, 3, 4, 0,
    CASE WHEN n % 7 = 0 THEN NULL WHEN n % 5 = 0 THEN 'UNKNOWN'
         WHEN n % 3 = 0 THEN 'PF00001-PF00002' ELSE 'PF00001' END,
    85, 90, 'workshop-synthetic'
FROM generate_series(1, 40) AS n;

INSERT INTO dpcstruct_mcs_properties
    (mc_id, mc_size, len_aa, len_std, len_ratio, plddt, disorder,
     tmscore, lddt, pident, pfam_score, pfam_da)
SELECT 'MC' || n, 0, 80, 0, 1,
    CASE n WHEN 1 THEN 0 WHEN 2 THEN 79.9 WHEN 3 THEN 80
           WHEN 4 THEN 100 WHEN 40 THEN NULL ELSE 60 + (n % 20) * 2 END,
    5, 0.8, 0.85, 35, 0.9,
    CASE WHEN n % 7 = 0 THEN NULL WHEN n % 5 = 0 THEN 'UNKNOWN' ELSE 'PF00002' END
FROM generate_series(1, 40) AS n;

INSERT INTO dpcfam_mcs_sequences (mcid, protein_id, seq_range, seq_length, aa_seq)
SELECT 'MC' || n, 'WS' || lpad(((n - 1) * 20 + member)::text, 6, '0'),
       '1-80', 80, repeat('ACDEFGHIKLMNPQRSTVWY', 4)
FROM generate_series(1, 40) AS n
CROSS JOIN LATERAL generate_series(1, CASE WHEN n = 1 THEN 130 ELSE 5 + (n % 10) * 3 END) AS member;

INSERT INTO dpcstruct_mcs_sequences (mc_id, protein_id, prot_range, prot_seq)
SELECT 'MC' || n, 'WS' || lpad(((n - 1) * 20 + member)::text, 6, '0'),
       '81-160', repeat('ACDEFGHIKLMNPQRSTVWY', 4)
FROM generate_series(1, 40) AS n
CROSS JOIN LATERAL generate_series(1, CASE WHEN n = 5 THEN 130 ELSE 4 + (n % 12) * 2 END) AS member;

INSERT INTO dpc_uniref50_pfam (uniref50_id, pfam_ids, pfam_ranges)
SELECT 'WS' || lpad(n::text, 6, '0'), 'PF00001', '1-80'
FROM generate_series(1, 800) AS n;

-- One known protein with >100 entries in EACH mapping table, for the PDF's
-- per-list response limit. Its artificial repeated domains fit within length 600.
INSERT INTO dpcfam_mcs_sequences (mcid, protein_id, seq_range, seq_length, aa_seq)
SELECT 'MC1', 'WSDEMO0001', ((n - 1) * 4 + 1) || '-' || (n * 4), 4, 'ACDE'
FROM generate_series(1, 130) AS n;
INSERT INTO dpcstruct_mcs_sequences (mc_id, protein_id, prot_range, prot_seq)
SELECT 'MC5', 'WSDEMO0001', ((n - 1) * 4 + 1) || '-' || (n * 4), 'ACDE'
FROM generate_series(1, 130) AS n;
INSERT INTO dpc_uniref50_pfam (uniref50_id, pfam_ids, pfam_ranges)
SELECT 'WSDEMO0001', 'PF00002', ((n - 1) * 4 + 1) || '-' || (n * 4)
FROM generate_series(1, 130) AS n;

INSERT INTO dpcfam_mcs_sequences (mcid, protein_id, seq_range, seq_length, aa_seq)
VALUES ('MC3', 'WSFAMONLY', '1-80', 80, repeat('ACDEFGHIKLMNPQRSTVWY', 4));
INSERT INTO dpcstruct_mcs_sequences (mc_id, protein_id, prot_range, prot_seq)
VALUES ('MC7', 'WSSTRUCTONLY', '81-160', repeat('ACDEFGHIKLMNPQRSTVWY', 4));
INSERT INTO dpc_uniref50_pfam (uniref50_id, pfam_ids, pfam_ranges)
VALUES ('WSPFAMONLY', 'PF00003', '1-80');

UPDATE dpcfam_mcs_properties AS mc SET size_uniref50 = (
    SELECT count(*) FROM dpcfam_mcs_sequences AS member WHERE member.mcid = mc.mcid
);
UPDATE dpcstruct_mcs_properties AS mc SET mc_size = (
    SELECT count(*) FROM dpcstruct_mcs_sequences AS member WHERE member.mc_id = mc.mc_id
);

-- A few synthetic annotations keep the app's CATH and SCOP tabs usable.
INSERT INTO dpcstruct_cath (cath_query, dpc_mcid, dpc_target, q_range, t_range,
                            qlen, tlen, qcov, tcov, alnlen, qtmscore, ttmscore, alntmscore, lddt, pident)
SELECT 'WS-CATH-' || n, 'MC' || n, 'WS' || lpad(((n - 1) * 20 + 1)::text, 6, '0'),
       '1-80', '81-160', 80, 80, 1, 1, 80, 0.8, 0.8, 0.8, 0.85, 35
FROM generate_series(1, 5) AS n;
INSERT INTO dpcstruct_scop (scop_query, dpc_mcid, dpc_target, q_range, t_range,
                            qlen, tlen, qcov, tcov, alnlen, qtmscore, ttmscore, alntmscore, lddt, pident)
SELECT 'WS-SCOP-' || n, 'MC' || n, 'WS' || lpad(((n - 1) * 20 + 1)::text, 6, '0'),
       '1-80', '81-160', 80, 80, 1, 1, 80, 0.8, 0.8, 0.8, 0.85, 35
FROM generate_series(1, 5) AS n;

CREATE INDEX idx_workshop_fam_protein ON dpcfam_mcs_sequences(protein_id);
CREATE INDEX idx_workshop_fam_mc ON dpcfam_mcs_sequences(mcid);
CREATE INDEX idx_workshop_struct_protein ON dpcstruct_mcs_sequences(protein_id);
CREATE INDEX idx_workshop_struct_mc ON dpcstruct_mcs_sequences(mc_id);
CREATE INDEX idx_workshop_pfam_protein ON dpc_uniref50_pfam(uniref50_id);
COMMIT;
ANALYZE;
