import matplotlib.pyplot as plt
import base64
from io import BytesIO
import seaborn as sns



def get_graph():
    buffer  = BytesIO()
    plt.savefig(buffer , format = 'png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph



def get_plot(x,y):
    plt.switch_backend('AGG')
    plt.style.use('ggplot')
    plt.figure(figsize=(10,5))
    plt.title('Analytics Of items')
    plt.plot(x,y,color = 'red', marker = 'o',linestyle='dashed')
    plt.plot([],[],color = 'red', marker = 'o',label=x, linewidth=1,linestyle='dashed')
    plt.plot([],[],color = 'red', marker = 'o',label=x, linewidth=1,linestyle='dashed')
    plt.xticks(rotation=90)
    plt.xlabel(' Item ')
    plt.ylabel('Price in INR₹')
    plt.tight_layout()
    graph = get_graph()
    return graph