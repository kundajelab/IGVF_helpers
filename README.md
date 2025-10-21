# Helper scripts for pseudobulking IGVF sc data

## Suggested workflow:

1.  Clean up a lab-submitted annotation to produce a tab-separated file with the following required columns:
-  Barcode column containing _only_ values corresponding to the barcode sequence. Call this column "cellBC_formatted"
-  Column with pseudobulk designation (e.g. cell type annotation)

2.  Create an account on the IGVF portal, and generate access/secret key to enable downloading files from the command line. See: [https://data.igvf.org/user-profile/](https://data.igvf.org/user-profile/)
3.  Identify analysis accession corresponding to a set of processed files on the IGVF portal. Example: [IGVFDS6955JCTX](https://data.igvf.org/analysis-sets/IGVFDS6955JCTX/). Note that you must be signed in to view the linked page.
4.  Prepare json with IGVFFs for downloading scATAC bed file and scRNA h5ad file. Example:
```
python get_igvf_download_accessions.py \
 -a IGVFDS6955JCTX \
 --access_key $ACCESS_KEY \
 --secret_key $SECRET_KEY \
 -o IGVFDS6955JCTX.json
```
5.  Download scRNA and scATAC data from portal. Example:
```
bash download_files.sh \
 --access_key $ACCESS_KEY \
 --secret_key $SECRET_KEY \
 --igvffs_in IGVFDS6955JCTX.json \
 --outdir .
```
6. Run pseudobulking on scATAC. Example:
```
python make_scATAC_pseudobulks.py \
 --annotations_in <path_to_annotations.tsv> \
 --cluster_col <name_of_col_with_clustering_ID> \
 --outpath <where_to_save_file> \
 --fragments_in <path_to_downloaded_fragments.bed.gz>
```
