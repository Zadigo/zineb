from zineb.app import Zineb
from zineb.models import fields
from zineb.extractors.links import LinkExtractor
from zineb.extractors.base import RowExtractor
from zineb.models.functions import concatenate
from zineb.models.datastructure import Model

class Player(Model):
    name = fields.CharField()
    birthdate = fields.DateField('%d.%m.%Y')
    height = fields.IntegerField()
    weight = fields.IntegerField()
    spike = fields.IntegerField()
    block = fields.IntegerField()
    profile = fields.UrlField()
    # image = fields.ImageField()
    # position = fields.CharField()


class Volleyball(Zineb):
    start_urls = [
        'http://www.fivb.org/EN/volleyball/competitions/WorldGrandPrix/2004/Teams/Teams.asp?sm=40'
    ]

    # def start(self):
    #     response = self.get_response(0)
    #     html = response.html_response
    #     links = html.links
    #     filtered_links = filter(lambda x: 'code=' in x, links)

    #     extractor = RowExtractor(has_headers=True)
    #     new_responses = response.follow_all(filtered_links)
    #     if new_responses:
    #         table_data = []
    #         for response in new_responses:
    #             tables = response.html_response.html_page.find_all('table')
    #             for table in tables:
    #                 width = table.attrs.get('width', 0)
    #                 if width == '631':
    #                     table_data.append(extractor.resolve(table))

    #         model = Player()
    #         if table_data:
    #             for data in table_data:
    #                 for row in data:
    #                     model.add_value('name', f'{row[2]} {row[3]}')
    #                     model.add_value('birthdate', row[5])
    #                     model.add_value('height', row[6])
    #                     model.add_value('weight', row[7])
    #                     model.add_value('spike', row[8])
    #                     model.add_value('block', row[9])

    #             model.save(filename='test.json')
    
    def start(self, response, **kwargs):
        request = kwargs.get('request')
        links = response.links

        filtered_links = list(filter(lambda x: 'code=' in x, links))
        new_responses = request.follow_all(filtered_links)
        
        if new_responses:
            model = Player()

            table_rows = []
            for response in new_responses:
                tables = response.html_response.html_page.find_all('table')
                for table in tables:
                    width = table.attrs.get('width', 0)
                    if width == '631':
                        rows = table.find_all('tr')
                        rows.pop(0)
                        for row in rows:
                            columns = row.find_all('td')
                            profile_link = columns[4].find('a').attrs.get('href')
                            # player_profile_response = request.follow(request.urljoin(profile_link))

                            model.add_value('name', concatenate(columns[2].text, columns[3].text))
                            # model.add_value('birthdate', columns[5].text)
                            model.add_value('height', columns[6].text)
                            model.add_value('weight', columns[7].text)
                            model.add_value('spike', columns[8].text)
                            model.add_value('block', columns[9].text)
                            model.add_value('profile', request.urljoin(profile_link))
                            # model.add_value('position', columns[7].text)

            model.save(filename='_test')

spider = Volleyball()
