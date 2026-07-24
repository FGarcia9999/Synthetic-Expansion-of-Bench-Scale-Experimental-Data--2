# Zenodo / GitHub release checklist

Repository strategy: **single GitHub release archived by Zenodo**.

Before creating the GitHub release:

1. Confirm that the active branch contains only PEERFIX2/CCE-facing files.
2. Confirm that historical PEERFIX1 materials remain only in `backup/pre-cce-v26-cleanup-peerfix1`.
3. Confirm dual licensing:
   - code: MIT;
   - data, figures, tables, manuscripts, and supplementary documents: CC BY 4.0.
4. Confirm author names and ORCIDs in `.zenodo.json` and `CITATION.cff`.
5. Upload final manuscript, supplementary material, figures, tables, and source code package.
6. Create a GitHub release from the clean PEERFIX2 branch.
7. Confirm that Zenodo archived the release and generated a DOI.
8. Update `README.md` and `CITATION.cff` with the Zenodo DOI if needed.
