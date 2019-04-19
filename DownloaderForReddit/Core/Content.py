"""
Downloader for Reddit takes a list of reddit users and subreddits and downloads content posted to reddit either by the
users or on the subreddits.


Copyright (C) 2017, Kyle Hickey


This file is part of the Downloader for Reddit.

Downloader for Reddit is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Downloader for Reddit is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Downloader for Reddit.  If not, see <http://www.gnu.org/licenses/>.
"""


import requests
from PyQt5.QtCore import QRunnable
import logging

from ..Utils import Injector, SystemUtil
from ..Logging import LogUtils


class Content(QRunnable):

    def __init__(self, url, text, user, post_title, subreddit, submission_id, number_in_seq, file_ext, save_path,
                 subreddit_save_method, date_created):
        """
        Class that holds information about a single file extracted from a reddit submission that is to be downloaded as
        content.  Also holes the method to download the file.

        :param url: The url that the file to be downloaded is located at
        :param user:  The reddit user who submitted to content to reddit
        :param subreddit:  The subreddit the content was submitted to
        :param submission_id:  The content identifier that is to be made part of the file name when the content is saved
                (e.g. the album id if the url is from an imgur album)
        :param number_in_seq:  The number of the file in a sequence of files (e.g. if the file is from an album)
        :param file_ext:  The extension of the file, used to save the file with the correct extension
        """
        super().__init__()
        self.logger = logging.getLogger('DownloaderForReddit.%s' % __name__)
        self.settings_manager = Injector.get_settings_manager()
        self.url = url
        self.text = text
        self.user = user
        self.post_title = post_title
        self.subreddit = subreddit
        self.submission_id = submission_id
        self.number_in_seq = number_in_seq
        self.file_ext = file_ext
        self.save_path = '%s%s' % (save_path, '/' if not save_path.endswith('/') else '')
        self.subreddit_save_method = subreddit_save_method
        self.date_created = date_created
        self.output = ''
        self.setAutoDelete(False)
        self.downloaded = False
        self.check_path = None

        self.queue = None

        if self.subreddit_save_method is None:
            self.filename = '%s%s%s%s' % (self.save_path, self.clean_filename(self.submission_id),
                                          self.number_in_seq, self.file_ext)
            self.check_path = self.save_path

        elif self.subreddit_save_method == 'User Name':
            self.filename = '%s%s/%s%s%s' % (self.save_path, self.user, self.clean_filename(self.submission_id),
                                             self.number_in_seq, self.file_ext)
            self.check_path = '%s%s/' % (self.save_path, self.user)

        elif self.subreddit_save_method == 'Subreddit Name':
            self.filename = '%s%s/%s%s%s' % (self.save_path, self.subreddit,
                                             self.clean_filename(self.submission_id), self.number_in_seq,
                                             self.file_ext)
            self.check_path = '%s%s' % (self.save_path, self.subreddit)

        elif self.subreddit_save_method == 'Subreddit Name/User Name':
            self.filename = '%s%s/%s/%s%s%s' % (self.save_path, self.subreddit, self.user,
                                                self.clean_filename(self.submission_id), self.number_in_seq,
                                                self.file_ext)
            self.check_path = '%s%s/%s/' % (self.save_path, self.subreddit, self.user)

        elif self.subreddit_save_method == 'User Name/Subreddit Name':
            self.filename = '%s%s/%s/%s%s%s' % (self.save_path, self.user, self.subreddit,
                                                self.clean_filename(self.submission_id), self.number_in_seq,
                                                self.file_ext)
            self.check_path = '%s%s/%s' % (self.save_path, self.user, self.subreddit)
        else:
            self.filename = '%s%s%s%s' % (self.save_path, self.clean_filename(self.submission_id),
                                          self.number_in_seq, self.file_ext)
            self.check_path = self.save_path

    def run(self):
        self.check_save_path_subreddit()
        try:
            if self.url is not None:
                self.download_url()
            if self.text is not None:
                self.download_text()
            self.set_file_modified_date()
            self.queue.put('Saved: %s' % self.filename)
            self.downloaded = True
            return None
        except ConnectionError:
            self.handle_connection_error()
        except:
            self.handle_exception()

    def download_url(self):
        """
        Downloads the data found at this content items url address and saves it as a file in the local file system.
        """
        response = requests.get(self.url, stream=True)
        if response.status_code == 200:
            with open(self.filename, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
        else:
            self.handle_unsuccessful_response(response.status_code)

    def download_text(self):
        """Saves the text found in this content items text attribute as a file in the local file system."""
        with open(self.filename, 'w') as file:
            file.write(self.text)

    def handle_unsuccessful_response(self, status_code):
        """Handles logging and output in case of a failed response from the server."""
        self.logger.warning('Failed Download: Unsuccessful response from server',
                            extra={'response_code': status_code, 'url': self.url, 'user': self.user,
                                   'submission_id': self.submission_id, 'number_in_seq': self.number_in_seq})
        self.queue.put('Failed Download:  File %s%s posted by %s failed to download...try link to download '
                       'manually: %s\n' % (self.submission_id, self.number_in_seq, self.user, self.url))

    def handle_connection_error(self):
        """Handles logging and output in case of a failed connection attempt to the server"""
        self.logger.error('Failed to establish a connection',
                          extra={'url': self.url, 'user': self.user, 'submission_id': self.submission_id,
                                 'number_in_seq': self.number_in_seq, 'extension': self.file_ext,
                                 'created': self.date_created}, exc_info=True)
        self.queue.put('Failed Download: Failed to establish a connection to url: %s\n'
                       'User: %s, Subreddit: %s, Title: %s' % (self.url, self.user, self.subreddit, self.post_title))

    def handle_exception(self):
        """Handles logging and output in case of a failed save due to a general exception."""
        self.logger.error('Failed to save content: Exception while saving file',
                          extra={'url': self.url, 'save_path': self.filename}, exc_info=True)
        self.queue.put('Failed to save content: %s' % self.filename)

    @staticmethod
    def clean_filename(name):
        """Ensures each file name does not contain forbidden characters and is within the character limit"""
        # For some reason the file system (Windows at least) is having trouble saving files that are over 180ish
        # characters.  I'm not sure why this is, as the file name limit should be around 240. But either way, this
        # method has been adapted to work with the results that I am consistently getting.
        forbidden_chars = '"*\\/\'.|?:<>'
        filename = ''.join([x if x not in forbidden_chars else '#' for x in name])
        if len(filename) >= 176:
            filename = filename[:170] + '...'
        return filename

    def check_save_path_subreddit(self):
        """
        Checks the supplied subreddit's check path and if it does not exist, creates the directory.
        """
        try:
            SystemUtil.create_directory(self.check_path)
        except PermissionError:
            self.logger.error('Could not create directory path for subreddit object',
                              extra={'path': self.check_path, 'subreddit': self.subreddit})

    def set_file_modified_date(self):
        """
        Sets the date modified of the created file to be the date the post was made on reddit.  First checks the
        settings manager to see if the user has this feature enabled.
        """
        if self.settings_manager.set_file_modified_date:
            try:
                SystemUtil.set_file_modify_time(self.filename, self.date_created)
            except Exception:
                if LogUtils.modified_date_log_count < 3:
                    self.settings_manager.modify_date_count += 1
                    self.queue.put('Could not set date modified for file: %s' % self.filename)
                    self.logger.error('Failed to set date modified for file', exc_info=True)

    def install_queue(self, queue):
        """
        Supplies an instance of the overall queue to every instance of this class so that the main GUI output box
        may be updated with the download progress from this class when it is moved to another thread
        """
        self.queue = queue
