from py2neo import Graph

def correct() -> None:
    graph=Graph(
            host='127.0.0.1',
            user='usr',
            password='medicalgraph2024'
            )
    graph.run("create (n:Anatomy{name:'肾脏'})")
    graph.run("match (n:Disease{name:'糖尿病肾病'}),(m:Anatomy{name:'肾脏'}) create (m)-[rel:Anatomy_Disease]->(n)")
    graph.run("match (n:Drug{name:'D PP-4i'}) detach delete (n)")
    graph.run("match (n:Drug{name:'糖尿病'}) detach delete (n)")
    graph.run("match (n:Test{name:'＜140／80mmHg'}) detach delete (n)")
    graph.run("match (n:Department{name:'肝炎'}) detach delete (n)")
    # print('Done.')

if __name__=='__main__':
    correct()