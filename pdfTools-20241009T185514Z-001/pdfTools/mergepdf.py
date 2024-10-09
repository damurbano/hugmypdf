# Función para agrupar los PDFs por directorio
def group_pdfs_by_directory(paths: list):
    grouped_paths = {}
    for path in paths:
        directory = path.parent
        if directory not in grouped_paths:
            grouped_paths[directory] = []
        grouped_paths[directory].append(path)
    return grouped_paths


# Función para mergear PDFs
def merge_pdfs(
    pdf_paths: list, output_path: Path, compression: int, show: bool = False
):
    merger = PdfMerger()
    for pdf in pdf_paths:
        merger.append(str(pdf))
    merger.add_metadata({'/Title': remove_parcial(pdf_paths[0])})
    merger.write(str(output_path))
    merger.close()
    compresspdf.compress_pdf(output_path, compression)
    if show:
        logger.info('Abriendo %s ...', output_path)
        _show_pdf(output_path)


# Función para obtener el directorio base común hasta /plugin_gen/
def get_base_directory(paths: list):
    for part in paths[0].parts:
        if part == 'plugin_gen':
            break
    return Path(*paths[0].parts[: paths[0].parts.index('plugin_gen') + 1])


# Función principal para agrupar, mergear y crear el archivo final
def process_pdfs(paths: list, compression: int = 0, show: bool = False):
    grouped_paths = group_pdfs_by_directory(paths)
    base_directory = get_base_directory(paths)

    merged_files = []
    for directory, pdf_list in grouped_paths.items():
        if len(pdf_list) > 1:
            output_path = directory / remove_parcial(pdf_list[0])
            logger.info(f"Mergeando parciales en: {output_path}")
            merge_pdfs(pdf_list, output_path, compression=compression)
            merged_files.append(output_path)
        else:
            merged_files.append(pdf_list[0])

    final_output_directory = base_directory / "mergedsPDFS"
    final_output_directory.mkdir(parents=True, exist_ok=True)
    final_output_path = final_output_directory / remove_parcial(pdf_list[0])
    paths_as_strings = [str(path) for path in merged_files]
    joined_string = ', '.join(paths_as_strings)
    logger.info(f"Mergeando: {joined_string}")
    merge_pdfs(merged_files, final_output_path, compression=compression, show=show)

    return merged_files, final_output_path


# Ordenar la lista por numeros de parciales
def get_parcial_number(path):
    match = re.search(r'Parcial (\d+)', path.name)
    if match:
        return int(match.group(1))
    else:
        return float('inf')  # Si no tiene "Parcial", colocarlo al final


def remove_parcial(path):
    new_name = re.sub(r' Parcial (\d+) y final', '', path.name).strip()
    new_name = re.sub(r' Parcial (\d+)', '', new_name).strip()
    return new_name if new_name else path.name
