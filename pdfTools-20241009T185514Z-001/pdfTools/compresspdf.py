#!/usr/bin/env python3
"""
Script de Python que utiliza ghoscript para comprimir ficheros PDF.
Niveles de compresión:
    0: defecto
    1: prepress
    2: printer
    3: ebook
    4: screen
Dependencias: Ghostscript.
"""

from pathlib import Path
import subprocess
import logging
import sys
import shutil

logger = logging.getLogger(__name__)


def compress_pdf(input_file_path: Path, power=3):
    """
    Script de Python que utiliza ghostcript para comprimir ficheros PDF.
    Niveles de compresión:
        0: defecto
        1: prepress
        2: printer
        3: ebook
        4: screen
    """
    quality = {
        0: '/default',
        1: '/prepress',
        2: '/printer',
        3: '/ebook',
        4: '/screen',
    }

    # Comprobamos si existe el fichero
    if not input_file_path.exists():
        logger.warning("Error: path invalido")
        sys.exit(1)

    # Comprobamos si es un pdf
    if input_file_path.suffix.lower() != '.pdf':
        logger.warning("Error: input file no es un PDF")
        sys.exit(1)

    output_file_path = input_file_path.parent.joinpath("compress.pdf")
    gs = get_ghostscript_path()
    logger.info("Comprimiendo PDF...")
    initial_size = input_file_path.stat().st_size
    subprocess.call(
        [
            gs,
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS={}'.format(quality[power]),
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            '-dEmbedAllFonts=true',
            '-dSubsetFonts=true',
            '-dColorImageDownsampleType=/Bicubic',
            '-dGrayImageDownsampleType=/Bicubic',
            '-dGrayImageResolution=144',
            '-dColorImageResolution=144',
            '-dMonoImageDownsampleType=/Bicubic',
            '-sOutputFile={}'.format(str(output_file_path)),
            input_file_path,
        ]
    )

    final_size = output_file_path.stat().st_size
    if final_size < initial_size:
        ratio = 1 - (final_size / initial_size)
        logger.info("Tamaño original {0:.1f}MB".format(initial_size / 1000000))
        logger.info("Comprimido un {0:.0%}.".format(ratio))
        logger.info("Tamaño final {0:.1f}MB".format(final_size / 1000000))
        logger.info("Reemplazando el pdf original...")
        # Reemplazo el pdf original:
        # Eliminamos el archivo original
        input_file_path.unlink()
        # Renombramos el archivo de salida al nombre del archivo original
        output_file_path.replace(input_file_path)
    else:
        logger.info(
            "La compression no fue realizada correctamente, se conserva el archivo original"
        )
    logger.info("Listo.")


def get_ghostscript_path():
    gs_names = ['gs', 'gswin32', 'gswin64']
    for name in gs_names:
        if shutil.which(name):
            return shutil.which(name)
    logger.warning(
        f'No GhostScript executable was found on path ({"/".join(gs_names)})'
    )
