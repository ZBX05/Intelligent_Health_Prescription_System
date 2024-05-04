from typing import Any

def list_type_answer(entity_list:list,query_data:list,question_code:int,unknown:str,too_long:int) -> str:
    if(len(query_data)==0):
        return unknown
    else:
        all_unknown=True
        for sub_list in query_data:
            if(len(sub_list)!=0):
                all_unknown=False
                break
        if(all_unknown==True):
            return unknown
    if(question_code==1):
        if(len(query_data)==1):
            return f'基于您的描述，您查询的疾病应该是{query_data[0]}。'
        else:
            return '基于您的描述，您查询的疾病应该是以下疾病或以下疾病中的一种：'+'、'.join(query_data)+'。'
    elif(question_code==2):
        if(len(entity_list)!=1):
            if(len(entity_list)>too_long):
                return '您同时询问的疾病过多，如果您有非常多的相关问题需要同时询问，请分多次提问。'
            answer='检测到您询问了多个疾病的病因，将为您分别提供参考回答：\n'
        else:
            answer=''
        for idx in range(len(entity_list)):
            if(len(query_data[idx])!=0):
                answer+=f'{entity_list[idx][0]}的病因有：'+'、'.join(query_data[idx])
            else:
                answer+=f'对于{entity_list[idx][0]}，我未能查询到相应的回答。'
            if(idx!=len(entity_list)-1):
                answer+='\n'
        return answer
    # elif(question_code==4):
    #     if(len(entity_list)>too_long):
    #             return '您同时询问的就医问题过多，如果您有非常多的相关问题需要同时询问，请分多次提问。'
    #     answer='对不起，为避免误诊，关于这个问题我只能为您提供间接的参考答案。\n'
    #     for idx in range(len(entity_list)):
    #         if(len(query_data[idx])!=0):
    #             answer+=f'{entity_list[idx][0]}可能需要的检查项目有：'+'、'.join(query_data[idx])
    #         else:
    #             answer+=f'对于{entity_list[idx][0]}，我未能查询到相应的回答。'+'。'
    #         if(idx!=len(entity_list)-1):
    #             answer+='\n'
    #     answer+='\n以上答案仅供参考，如有就医需要，可根据检查项目查询相关的医院并提前进行咨询。'
    #     return answer
    # elif(question_code==6):
    #     if(len(entity_list)!=1):
    #         if(len(entity_list)>too_long):
    #             return '您同时询问的疾病过多，如果您有非常多的相关问题需要同时询问，请分多次提问。'
    #         answer='检测到您询问了多个疾病的症状，将为您分别提供参考回答：\n'
    #     else:
    #         answer=''
    #     for idx in range(len(entity_list)):
    #         if(len(query_data[idx])!=0):
    #             answer+=f'{entity_list[idx][0]}的症状有：'+'、'.join(query_data[idx])+'。'
    #         else:
    #             answer+=f'对于{entity_list[idx][0]}，我未能查询到相应的回答。'
    #         if(idx!=len(entity_list)-1):
    #             answer+='\n'
    #     return answer
    elif(question_code==7):
        if(len(entity_list)!=1):
            if(len(entity_list)>too_long):
                return '您同时询问的药物或治疗方法过多，如果您有非常多的相关问题需要同时询问，请分多次提问。'
            answer='检测到您询问了种药物或治疗方法所针对的疾病，将为您分别提供参考回答：\n'
        else:
            answer=''
        for idx in range(len(entity_list)):
            if(len(query_data[idx])!=0):
                answer+=f'{entity_list[idx][0]}主要针对的疾病有：'+'、'.join(query_data[idx])+'。'
            else:
                answer+=f'对于{entity_list[idx][0]}，我未能查询到相应的回答。'
            if(idx!=len(entity_list)-1):
                answer+='\n'
        return answer
    elif(question_code==8):
        if(len(entity_list)!=1):
            if(len(entity_list)>too_long):
                return '您同时询问的药物过多，如果您有非常多的相关问题需要同时询问，请分多次提问。'
            answer='检测到您询问了种药物的不良反应，将为您分别提供参考回答：\n'
        else:
            answer=''
        for idx in range(len(entity_list)):
            if(len(query_data[idx])!=0):
                answer+=f'{entity_list[idx][0]}可能存在的不良反应有：'+'、'.join(query_data[idx])+'。'
            else:
                answer+=f'对于{entity_list[idx][0]}，我未能查询到相应的回答。'
            if(idx!=len(entity_list)-1):
                answer+='\n'
        return answer
    elif(question_code==0):
        answer='对于您提出的问题我无法给出确定的参考答案，但是检测到您输入的问句中包含检查项目，我将试着给出检查项目针对的疾病：\n'
        for idx in range(len(entity_list) if len(entity_list)<=too_long else too_long):
            if(len(query_data[idx])!=0):
                answer+=f'{entity_list[idx][0]}针对的疾病有：'+'、'.join(query_data[idx])+'。'
            else:
                answer+=f'对于{entity_list[idx][0]}，我未能查询到相应的回答。'
            if(idx!=len(entity_list)-1):
                answer+='\n'
        answer+='您的问题很有可能超出了我的知识范围，若回答不准确则请继续就其他方面进行提问，或试着使用更清晰、更规范的语言描述问题。'
        return answer

def medical_answer(medical_dict:dict) -> str:
    test,department=medical_dict["test"],medical_dict["department"]
    answer=''
    unknown_list=[]
    if(len(test)!=0):
        answer+='可能需要的检查项目有：'+'、'.join(test)+'；'+'\n'
    else:
        unknown_list.append('检查项目')
    if(len(department)!=0):
        answer+='挂号科室有：'+'、'.join(department)+'。'+'\n'
    else:
        unknown_list.append('挂号科室')
    if(len(unknown_list)!=0 and len(unknown_list)!=4):
        answer+='我未能查询到关于'+'、'.join(unknown_list)+'的内容。\n'
    elif(len(unknown_list)==4):
        return '我未能查询到任何治疗方案。\n'
    return '\n'+answer
    

def cure_answer(cure_dict:dict) -> str:
    treatment,drug,operation,sport=cure_dict["treatment"],cure_dict["drug"],cure_dict["operation"],cure_dict["sport"]
    answer=''
    unknown_list=[]
    if(len(treatment)!=0):
        answer+='非手术治疗有：'+'、'.join(treatment)+'；'+'\n'
    else:
        unknown_list.append('非手术治疗方案')
    if(len(drug)!=0):
        answer+='适用药物有：'+'、'.join(drug)+'；'+'\n'
    else:
        unknown_list.append('适用药物')
    if(len(operation)!=0):
        answer+='治疗手术有：'+'、'.join(operation)+'；'+'\n'
    else:
        unknown_list.append('治疗手术')
    if(len(sport)!=0):
        answer+='推荐的运动有：'+'、'.join(sport)+'。'+'\n'
    else:
        unknown_list.append('推荐运动')
    if(len(unknown_list)!=0 and len(unknown_list)!=4):
        answer+='我未能查询到关于'+'、'.join(unknown_list)+'的内容。\n'
    elif(len(unknown_list)==4):
        return '我未能查询到任何治疗方案。\n'
    return '\n'+answer

def dict_type_answer(entity_list:list,query_data:dict,question_code:int,unknown:str,too_long:int) -> str:
    answer=unknown
    if(len(query_data)==0):
        return unknown
    if(question_code==3):
        all_unknown=True
        for sub_list_1,sub_list_2,sub_list_3,sub_list_4 in zip(query_data["treatment"],query_data["drug"],query_data["operation"],query_data["sport"]):
            if(len(sub_list_1)!=0 or len(sub_list_2)!=0 or len(sub_list_3)!=0 or len(sub_list_4)!=0):
                all_unknown=False
                break
        if(all_unknown==True):
            return unknown
        treatment,drug,operation,sport=query_data["treatment"],query_data["drug"],query_data["operation"],query_data["sport"]
        if(len(entity_list)!=1):
            if(len(entity_list)>too_long):
                return '您同时询问的疾病过多，如果您有非常多的相关问题需要同时询问，请分多次提问。'
            answer='检测到您询问了多个疾病的治疗方案，将为您分别提供参考回答：\n'
        else:
            answer=''
        for idx in range(len(entity_list)):
            answer+=f'对于{entity_list[idx][0]}，'
            answer+=cure_answer({"treatment":treatment[idx],"operation":operation[idx],"drug":drug[idx],"sport":sport[idx]})
            # if(len(treatment[idx])==0 and len(drug[idx])==0 and len(operation[idx])==0 and len(sport[idx])==0):
            #     unknown_list.append(entity_list[idx])
            # else:
            #     answer+=f'对于{entity_list[idx][0]}，'
            #     answer+=cure_answer({"treatment":treatment[idx],"operation":operation[idx],"drug":drug[idx],"sport":sport[idx]})
    if(question_code==4):
        all_unknown=True
        for sub_list_1,sub_list_2 in zip(query_data["test"],query_data["department"]):
            if(len(sub_list_1)!=0 or len(sub_list_2)!=0):
                all_unknown=False
                break
        if(all_unknown==True):
            return unknown
        test,department=query_data["test"],query_data["department"]
        if(len(entity_list)!=1):
            if(len(entity_list)>too_long):
                return '您同时询问的就医问题过多，如果您有非常多的相关问题需要同时询问，请分多次提问。'
        answer='对不起，为避免误诊，关于这个问题我只能为您提供间接的参考答案。\n'
        for idx in range(len(entity_list)):
            answer+=f'对于{entity_list[idx][0]}，'
            answer+=medical_answer({"test":test[idx],"department":department[idx]})
        answer+='以上答案仅供参考，如有就医需要，可根据检查项目查询相关的医院并提前进行咨询。'
    if(question_code==6):
        all_unknown=True
        for sub_list_1 in query_data["symptom"]:
            if(len(sub_list_1)!=0):
                all_unknown=False
                break
        if(all_unknown==True):
            return unknown
        symptom,infectivity,period=query_data["symptom"],query_data["infectivity"],query_data["period"]
        if(len(entity_list)!=1):
            if(len(entity_list)>too_long):
                return '您同时询问的疾病过多，如果您有非常多的相关问题需要同时询问，请分多次提问。'
            answer='检测到您询问了多个疾病的症状，将为您分别提供参考回答：\n'
        else:
            answer=''
        for idx in range(len(entity_list)):
            if(len(symptom[idx])==0 and len(infectivity[idx])==0 and len(period[idx])==0):
                answer+=f'对于{entity_list[idx][0]}，我未能查询到相应的回答。'
                continue
            if(len(symptom[idx])!=0):
                answer+=f'{entity_list[idx][0]}的症状有：'+'、'.join(symptom[idx])+'。'
            else:
                answer+=f'对于{entity_list[idx][0]}，我未能查询对应的症状。'
            if(len(infectivity[idx])!=0):
                answer+=f'{entity_list[idx][0]}的传染性为：'+infectivity[idx][0]+'。'
            if(len(period[idx])!=0):
                answer+=f'{entity_list[idx][0]}的平均医学治疗周期为：'+period[idx][0]+'。'
            if(idx!=len(entity_list)-1):
                answer+='\n'
    return answer

class Generator:
    def __init__(self,unknown:str,too_long:int) -> None:
        self.unknown=unknown
        self.too_long=too_long

    def generate(self,entity_list:list,query_data:Any,question_code:int) -> str:
        if(query_data is None):
            return self.unknown
        if(isinstance(query_data,list)):
            generator_text=list_type_answer(entity_list,query_data,question_code,self.unknown,self.too_long)
            if(generator_text[-1]=='\n'):
                generator_text=generator_text[:-1]
        elif(isinstance(query_data,dict)):
            generator_text=dict_type_answer(entity_list,query_data,question_code,self.unknown,self.too_long)
            if(generator_text[-1]=='\n'):
                generator_text=generator_text[:-1]
        return generator_text
    
    def __call__(self,entity_list:list,query_data:Any,question_code:int) -> str:
        return self.generate(entity_list,query_data,question_code)

        
