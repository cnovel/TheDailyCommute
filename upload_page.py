"""Upload a page via FTP"""
import ftplib
import logging


class FtpConfig:
    """Store the FTP configuration for uploading the Daily Commute"""
    def __init__(self, url: str, usr: str, pwd: str, directory: str):
        self._url = url
        self._usr = usr
        self._pwd = pwd
        self._dir = directory

    def url(self) -> str:
        """
        Get FTP url
        :return: url
        """
        return self._url

    def usr(self) -> str:
        """
        Get FTP user name
        :return: user name
        """
        return self._usr

    def pwd(self) -> str:
        """
        Get FTP password
        :return: password
        """
        return self._pwd

    def dir(self) -> str:
        """
        Get FTP directory where the Daily Commute is saved
        :return: directory
        """
        return self._dir


def upload_to(ftp_config, filename):
    """
    Upload a file via FTP
    :param ftp_config: FTP configuration
    :param filename: File to upload
    :return: bool
    """
    try:
        logging.info(f'Connecting to {ftp_config.url()} with user {ftp_config.usr()}')
        session = ftplib.FTP(ftp_config.url(), ftp_config.usr(), ftp_config.pwd())
        logging.info(f'Navigating to {ftp_config.dir()}')
        session.cwd(ftp_config.dir())
        logging.info(f'Uploading {filename}...')
        with open(filename, 'rb') as file:
            session.storbinary('STOR index.html', file)
        session.quit()
        logging.info('The Daily Commute was posted')
        return True
    except Exception as exc:
        logging.exception(exc)
        return False
