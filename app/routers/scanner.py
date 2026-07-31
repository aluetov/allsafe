from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
import dns.rdatatype
import dns.rdataclass
import dns.asyncresolver
import dns.resolver
import json
from ..db.models import Domain
from ..db.db import Session
from ..redis.redis import redis


router = APIRouter()

resolver = dns.asyncresolver.Resolver()
resolver.nameservers = ['8.8.8.8']

class DomainRequest(BaseModel):
    domain: str = Field(
        ..., 
        pattern=r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="A valid domain name to scan"
    )

@router.post("/scan")
async def scan_dns(request: DomainRequest):
    #check whether dns exists in redis
    cached_key = f"dns:{request.domain}"
    cached_response = await redis.get(cached_key)
    if cached_response is not None:
        print('Cache hit')
        return json.loads(cached_response)
    print("Cache MISS")


    try:
        answer_for_A = await resolver.resolve(request.domain, "A", lifetime=3.0) # send dns resolve request if there is no domain in redis
        
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        raise HTTPException(status_code=404, detail="No A record found for this domain") from None
        
    except (dns.resolver.LifetimeTimeout, dns.resolver.NoNameservers):
        raise HTTPException(status_code=502, detail="DNS was slow or unreachable") from None
        
    except dns.resolver.YXDOMAIN:
        raise HTTPException(status_code=400, detail="Name malformed/too long") from None


    answer_dict = { #build the response
        "qname": answer_for_A.qname.to_text(),
        "canonical_name": answer_for_A.canonical_name.to_text(),
        "record_type": dns.rdatatype.to_text(answer_for_A.rdtype),
        "record_class": dns.rdataclass.to_text(answer_for_A.rdclass),
        "expiration": answer_for_A.expiration,
        "records": [record.to_text() for record in answer_for_A]
    }


    await redis.set( #set in redis before adding to postgres
        cached_key,
        json.dumps(answer_dict),
        ex=300
    )


    domain = Domain(
        qname=answer_dict['qname'], canonical_name=answer_dict['canonical_name'],
        record_type=answer_dict['record_type'], record_class=answer_dict['record_class'], 
        expiration=answer_dict['expiration'], records=answer_dict['records']
    )

    async with Session.begin() as session: #add domain to postgres
        session.add(domain)

    return answer_dict

@router.get("/check/{domain}")
async def check_domain(domain: str):
    cache_key = f"dns:{domain}"
    cached_response = await redis.get(cache_key)
    if cached_response is not None:
        print('Cache hit')
        ttl = await redis.ttl(cache_key)
        response = {
            "source": "redis",
            'ttl': ttl,
            'cached_response': json.loads(cached_response)
        }
        return response
    print('not in cache')


    async with Session.begin() as session:
        stmt = (
            select(Domain)
            .where(Domain.qname == f"{domain}.")
            .order_by(Domain.id.desc())
        )
        result = await session.execute(stmt)
        db_domain = result.scalars().first()
        if db_domain is None:
            raise HTTPException(
                status_code=404,
                detail="Domain not found"
            )

        response = {
            "qname": db_domain.qname,
            "canonical_name": db_domain.canonical_name,
            "record_type": db_domain.record_type,
            "record_class": db_domain.record_class,
            "expiration": db_domain.expiration,
            "records": db_domain.records,
        }

        await redis.set(
                    cache_key,
                    json.dumps(response),
                    ex=300,
                )

        return {
            "source": "postgres",
            "data": response,
        }
    