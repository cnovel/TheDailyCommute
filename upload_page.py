"""Upload a page via FTP"""
import ftplib
import logging


def upload_to(server, usr, pwd, directory, filename):
    """
    Upload a file via FTP
    :param server: server url
    :param usr: username
    :param pwd: password
    :param directory: where to upload the file
    :param filename: file to upload
    :return: bool
    """
    try:
        logging.info(f'Connecting to {server} with user {usr}')
        session = ftplib.FTP(server, usr, pwd)
        logging.info(f'Navigating to {directory}')
        session.cwd(directory)
        logging.info(f'Uploading {filename}...')
        with open(filename, 'rb') as file:
            session.storbinary('STOR index.html', file)
        session.quit()
        logging.info('The Daily Commute was posted')
        return True
    except Exception as exc:
        logging.exception(exc)
        return False
