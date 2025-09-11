# About

Welcome! This repository hosts code and content for an experimental "living synthesis" optimized for synthesis of ideas around new infrastructures for common knowledge. 

The living synthesis is structured around a "discourse graph" of claims, evidence, and arguments that can be recombined in various ways to surface new insights. The goal is to explore how we can better structure and share knowledge in a way that is open, collaborative, and dynamic.

The code for this living synthesis is based on the popular [Quartz](https://quartz.jzhao.xyz/) static site generator, which allows for easy publishing of markdown content with rich metadata, and the creation of custom components and plugins. Many thanks to Defender of Basic for creating the Quartz template and [tutorial](https://dev.to/defenderofbasic/host-your-obsidian-notebook-on-github-pages-for-free-8l1) we used to set this up, and to Jacky Zhao for creating Quartz, which is the static site generator used in this template.

## Current structure of the repository

The parent structure is the code for a static site generator (Quartz) that builds a website from markdown files in the `content/` directory.

Inside `content/` are two main directories:
- `Posts/`
	- Houses the ever-evolving and unstable "front page" where ideas are being developed and/or recombined. some posts here will be microblogs, snapshots in time. The content here probably won't be updated directly, since they are snapshots in time.
- `DiscourseGraph/`
	- Hosts the more stable and mature "knowledge base" that the ideas will draw from and develop. some subset of these nodes will also be mirror/micropublished

## How to contribute

Contributions are very welcome! There are probably some open issues from both a code or content perspective. More on this soon.

### Ideas / backlog

This is an experimental system in addition to hosting content. Some things we'd like to experiment with include:
- One or more "views" that aggregate around certain subsets of the discourse graph, as more digestible entry points.
	- These may later evolve into formal "arguments" or "syntheses" that more formally combine discourse nodes in structured ways that surface their evidential and argument structure.
- Spatial/interactive "views"
- More focused UIs within claims that clearly detail their underlying evidence.

As the ideas mature, they'll peel off into issues and maybe even projects or tags in this repo.