from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import dns.rdatatype
import dns.rdataclass
import dns.asyncresolver
import dns.resolver
from ..db.models import Domain
from ..db.db import Session

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
    try:
        answer_for_A = await resolver.resolve(request.domain, "A", lifetime=3.0)
        
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        raise HTTPException(status_code=404, detail="No A record found for this domain") from None
        
    except (dns.resolver.LifetimeTimeout, dns.resolver.NoNameservers):
        raise HTTPException(status_code=502, detail="DNS was slow or unreachable") from None
        
    except dns.resolver.YXDOMAIN:
        raise HTTPException(status_code=400, detail="Name malformed/too long") from None

    answer_dict = {
        "qname": answer_for_A.qname.to_text(),
        "canonical_name": answer_for_A.canonical_name.to_text(),
        "record_type": dns.rdatatype.to_text(answer_for_A.rdtype),
        "record_class": dns.rdataclass.to_text(answer_for_A.rdclass),
        "expiration": answer_for_A.expiration,
        "records": [record.to_text() for record in answer_for_A]
    }

    domain = Domain(
        qname=answer_dict['qname'], canonical_name=answer_dict['canonical_name'],
        record_type=answer_dict['record_type'], record_class=answer_dict['record_class'], 
        expiration=answer_dict['expiration'], records=answer_dict['records']
    )

    async with Session.begin() as session:
        session.add(domain)

    return answer_dict
