# Analysis Questions

1. **Which subnet has the most hosts?**  
- `10.15.4.0/22` with 1022 usable hosts  

2. **Are there any overlapping subnets?**  
- No overlapping subnets found.  

3. **What is the smallest and largest subnet in terms of address space?**  
- Smallest: `10.0.3.0/24` (256 total addresses)  
- Largest: `10.15.4.0/22` (1024 total addresses)  

4. **Suggest a subnetting strategy to reduce wasted IPs in this network.**  
- Adopt **VLSM** (Variable-Length Subnet Masking) to size each block precisely.  
- **Aggregate** contiguous subnets for route summarization.  
- **Right-size** any large `/22` into smaller `/23` or `/24` to reclaim unused space.  
