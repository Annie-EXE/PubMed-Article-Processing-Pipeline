import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element


def get_author_info_from_article_num(root: Element, article_num: int):

    article = root.findall(".//PubmedArticle")[article_num]

    title = article.find(".//ArticleTitle").text
    pmid = article.find(".//PMID").text
    year = article.find(".//PubDate/Year").text

    keyword_list = [keyword.text for keyword in article.findall(".//KeywordList/Keyword")]

    mesh_list = [mesh.text for mesh in article.findall(".//MeshHeading/DescriptorName[@UI]")]

    authors = article.findall(".//AuthorList/Author")
    
    authors_info = []
    
    for author in authors:

        forename = author.find(".//ForeName").text if author.find(".//ForeName") is not None else ""
        lastname = author.find(".//LastName").text if author.find(".//LastName") is not None else ""
        initials = author.find(".//Initials").text if author.find(".//Initials") is not None else ""
        identity = author.find(".//AffiliationInfo/Identifier[@Source='GRID']").text if author.find(".//AffiliationInfo/Identifier[@Source='GRID']") is not None else ""

        affiliation_list = [aff.text for aff in author.findall(".//Affiliation")]

        # affilitaiton_list = []

        # for aff in author.findall(".//Affiliation"):

        author_info = {
            "forename": forename,
            "lastname": lastname,
            "initials": initials,
            "identity": identity,
            "affiliation": affiliation_list
        }
        authors_info.append(author_info)
    
    return authors_info


def get_all_author_data_for_each_article(root, article_cap):

    author_data = []

    for i in range(article_cap):

        author_data.append(get_author_info_from_article_num(root, i))


if __name__ == "__main__":

    tree = ET.parse("pubmed_result_sjogren.xml")

    root = tree.getroot()

    article_cap = len(root.findall(".//PubmedArticle"))

    author_data = get_all_author_data_for_each_article(root, article_cap)

