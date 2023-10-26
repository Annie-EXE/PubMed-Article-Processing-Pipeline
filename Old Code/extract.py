import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element


def find_num_articles(root: Element):

    num_articles = len(root.findall(".//PubmedArticle"))

    return num_articles


def get_data_for_specified_article(root: Element, article_number: int):

    article = root.findall(".//PubmedArticle")[article_number]

    title = article.find(".//ArticleTitle").text
    pmid = article.find(".//PMID").text
    year = article.find(".//PubDate/Year").text

    keyword_list = [keyword.text for keyword in article.findall(".//KeywordList/Keyword")]

    mesh_list = [mesh.text for mesh in article.findall(".//MeshHeading/DescriptorName[@UI]")]

    output = {
        "title": title,
        "pmid": pmid,
        "year": year,
        "keyword_list": keyword_list,
        "mesh_list": mesh_list
    }

    return output


def get_author_info_from_article_num(root: Element, article_num: int):

    article = root.findall(".//PubmedArticle")[article_num]

    authors = article.findall(".//AuthorList/Author")
    
    authors_info = []
    
    for author in authors:
        forename = author.find(".//ForeName").text
        lastname = author.find(".//LastName").text
        initials = author.find(".//Initials").text
        identity = author.find(".//AffiliationInfo/Identifier[@Source='GRID']").text
        affiliation_list = [aff.text for aff in author.findall(".//Affiliation")]

        author_info = {
            "forename": forename,
            "lastname": lastname,
            "initials": initials,
            "identity": identity,
            "affiliation": affiliation_list
        }
        authors_info.append(author_info)
    
    return authors_info



def get_data_for_specified_article_incl_authors(root: Element, article_number: int):

    article = root.findall(".//PubmedArticle")[article_number]

    title = article.find(".//ArticleTitle").text
    pmid = article.find(".//PMID").text
    year = article.find(".//PubDate/Year").text

    keyword_list = [keyword.text for keyword in article.findall(".//KeywordList/Keyword")]

    mesh_list = [mesh.text for mesh in article.findall(".//MeshHeading/DescriptorName[@UI]")]

    authors = article.findall(".//AuthorList/Author")
    
    authors_info = []
    
    for author in authors:
        forename = author.find(".//ForeName").text
        lastname = author.find(".//LastName").text
        initials = author.find(".//Initials").text
        identity = author.find(".//AffiliationInfo/Identifier[@Source='GRID']").text
        affiliation_list = [aff.text for aff in author.findall(".//Affiliation")]

        author_info = {
            "forename": forename,
            "lastname": lastname,
            "initials": initials,
            "identity": identity,
            "affiliation": affiliation_list
        }
        authors_info.append(author_info)

    output = {
        "title": title,
        "pmid": pmid,
        "year": year,
        "keyword_list": keyword_list,
        "mesh_list": mesh_list,
        "authors_info": authors_info
    }

    return output



def get_author_info_from_full_name(root: Element, author_name: str):

    name_split = author_name.split(" ")

    if len(name_split) < 2:

        raise ValueError("Full name must be provided")

    authors = root.findall(".//Author")

    possible_authors = []
    
    for author in authors:
        if author[0]:
            author_forename = author[0].text
            author_lastname = author.find(".//LastName").text
            if author_forename == name_split[0] and author_lastname == name_split[-1]:
                possible_authors.append(author)
    
    if len(possible_authors) == 0:
        return "Author not found"
    
    authors_info = []

    for author in authors:
        forename = author.find(".//ForeName").text
        lastname = author.find(".//LastName").text
        initials = author.find(".//Initials").text
        identity = author.find(".//AffiliationInfo/Identifier[@Source='GRID']").text
        affiliation_list = [aff.text for aff in author.findall(".//Affiliation")]

        author_info = {
            "forename": forename,
            "lastname": lastname,
            "initials": initials,
            "identity": identity,
            "affiliation": affiliation_list
        }
        authors_info.append(author_info)
    
    return authors_info


if __name__ == "__main__":

    tree = ET.parse("pubmed_result_sjogren.xml")

    root = tree.getroot()

    print(type(root))

    # Task 1

    print("Number of articles:", find_num_articles(root))

    # Task 2

    try:

        article_num = int(input("Select an article number: "))
    
    except:

        print("Valid article number must be provided.")
    
    print(get_data_for_specified_article(root, article_num))

    # Task 3

    get_author_method = input("""\nChoose method to fetch author(s): 
                              articlenum/authorname/identity \n""")
    
    if get_author_method == "articlenum":

        try:

            article_num_auth = int(input("""\n\nSelect an article number to 
                                retrieve author info: \n"""))
            
            print("Author(s): ", get_author_info_from_article_num(root, article_num_auth))
    
        except:

            print("Valid article number must be provided.")
        
    if get_author_method == "authorname":

        author_name = input("""\nEnter author's full name: \n""")
            
        print("Author(s): ", get_author_info_from_full_name(root, author_name))


