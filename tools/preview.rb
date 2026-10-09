#!/usr/bin/env ruby
# frozen_string_literal: true
#
# A deliberately small stand-in for `jekyll build`, used to preview and
# sanity-check this site on machines where the full Jekyll toolchain will not
# install (it needs native extensions, and therefore ruby-dev).
#
# It implements only the subset of Jekyll this site actually uses: front matter,
# layouts, _data, `include` with parameters, and the relative_url /
# absolute_url / markdownify filters.
#
#   ruby tools/preview.rb [output_dir]
#
# GitHub Pages still builds the site with real Jekyll; this is for local eyes.

require 'yaml'
require 'fileutils'
require 'liquid'
require 'kramdown'
require 'kramdown-parser-gfm'

ROOT = File.expand_path('..', __dir__)
OUT  = ARGV[0] || File.join(ROOT, '_site_preview')

def deep_stringify(obj)
  case obj
  when Hash  then obj.each_with_object({}) { |(k, v), h| h[k.to_s] = deep_stringify(v) }
  when Array then obj.map { |v| deep_stringify(v) }
  else obj
  end
end

def read_front_matter(path)
  raw = File.read(path)
  if raw.start_with?('---')
    parts = raw.split(/^---\s*$/, 3)
    data = YAML.safe_load(parts[1], permitted_classes: [Date, Time], aliases: true) || {}
    [deep_stringify(data), parts[2].to_s.sub(/\A\n/, '')]
  else
    [{}, raw]
  end
end

def markdownify(text)
  Kramdown::Document.new(text.to_s, input: 'GFM', auto_ids: true, hard_wrap: false,
                                    smart_quotes: %w[lsquo rsquo ldquo rdquo]).to_html
end

# --- config and data ---------------------------------------------------------

CONFIG = deep_stringify(YAML.safe_load(File.read(File.join(ROOT, '_config.yml')),
                                       permitted_classes: [Date, Time], aliases: true))
BASEURL = CONFIG['baseurl'].to_s
SITEURL = CONFIG['url'].to_s

DATA = Dir[File.join(ROOT, '_data', '*.yml')].each_with_object({}) do |f, h|
  h[File.basename(f, '.yml')] =
    deep_stringify(YAML.safe_load(File.read(f), permitted_classes: [Date, Time], aliases: true))
end

# --- Liquid extensions -------------------------------------------------------

module SiteFilters
  def relative_url(input)
    s = input.to_s
    return s if s.empty? || s.start_with?('http://', 'https://', '//', 'mailto:')
    BASEURL + (s.start_with?('/') ? s : "/#{s}")
  end

  def absolute_url(input)
    s = input.to_s
    return s if s.start_with?('http://', 'https://', 'mailto:')
    SITEURL + relative_url(s)
  end

  def markdownify(input)
    Kramdown::Document.new(input.to_s, input: 'GFM', auto_ids: true, hard_wrap: false,
                                       smart_quotes: %w[lsquo rsquo ldquo rdquo]).to_html
  end
end
Liquid::Template.register_filter(SiteFilters)

# Jekyll allows unquoted include names and key=value parameters; stock Liquid
# does not, so swap in a tag that matches Jekyll's behaviour.
class JekyllInclude < Liquid::Tag
  SYNTAX = /([\w\-\/.]+)(.*)/m

  def initialize(tag_name, markup, options)
    super
    m = markup.strip.match(SYNTAX)
    raise Liquid::SyntaxError, "bad include: #{markup}" unless m

    @file = m[1]
    @params = m[2].to_s.scan(/(\w+)\s*=\s*("[^"]*"|'[^']*'|[^\s]+)/)
  end

  def render(context)
    path = File.join(ROOT, '_includes', @file)
    raise "missing include: #{@file}" unless File.exist?(path)

    params = @params.each_with_object({}) do |(k, v), h|
      h[k] = if v =~ /\A["'](.*)["']\z/ then Regexp.last_match(1)
             else context[v]
             end
    end
    partial = Liquid::Template.parse(File.read(path))
    context.stack do
      context['include'] = params
      partial.render!(context)
    end
  end
end
Liquid::Template.register_tag('include', JekyllInclude)

# {% feed_meta %} is supplied by jekyll-feed in the real build.
class FeedMeta < Liquid::Tag
  def render(_context)
    %(<link type="application/atom+xml" rel="alternate" ) +
      %(href="#{SITEURL}#{BASEURL}/feed.xml" title="#{CONFIG['title']}">)
  end
end
Liquid::Template.register_tag('feed_meta', FeedMeta)

# --- collect documents -------------------------------------------------------

def slugify(name) = name.gsub(/\.(md|html)\z/, '')

pages = Dir[File.join(ROOT, '_pages', '*.{md,html}')].sort.map do |f|
  fm, body = read_front_matter(f)
  url = fm['permalink'] || "/#{slugify(File.basename(f))}/"
  fm.merge('content' => body, 'url' => url,
           'layout' => fm['layout'] || 'page',
           'ext' => File.extname(f))
end

SITE = CONFIG.merge(
  'data' => DATA,
  'pages' => pages,
  'time' => Time.now
)

# --- render ------------------------------------------------------------------

LAYOUTS = Dir[File.join(ROOT, '_layouts', '*.html')].each_with_object({}) do |f, h|
  fm, body = read_front_matter(f)
  h[File.basename(f, '.html')] = { 'fm' => fm, 'body' => body }
end

def render_doc(doc)
  payload = { 'site' => SITE, 'page' => doc }
  out = Liquid::Template.parse(doc['content']).render!(payload, strict_variables: false)
  out = markdownify(out) if doc['ext'] == '.md'

  layout_name = doc['layout']
  seen = []
  while layout_name && LAYOUTS[layout_name]
    raise "layout loop at #{layout_name}" if seen.include?(layout_name)

    seen << layout_name
    layout = LAYOUTS[layout_name]
    out = Liquid::Template.parse(layout['body'])
                          .render!(payload.merge('content' => out), strict_variables: false)
    layout_name = layout['fm']['layout']
  end
  out
end

FileUtils.rm_rf(OUT)
FileUtils.mkdir_p(OUT)

errors = []
pages.each do |doc|
  begin
    html = render_doc(doc)
  rescue StandardError => e
    errors << "#{doc['url']}: #{e.class}: #{e.message}"
    next
  end
  url = doc['url']
  dest = if url.end_with?('/') then File.join(OUT, url, 'index.html')
         else File.join(OUT, url)
         end
  FileUtils.mkdir_p(File.dirname(dest))
  File.write(dest, html)
  puts "  #{url}"
end

# copy static assets so the preview renders with real CSS and images
%w[assets images files].each do |dir|
  src = File.join(ROOT, dir)
  FileUtils.cp_r(src, OUT) if Dir.exist?(src)
end

if errors.empty?
  puts "\nOK — #{pages.size} documents rendered into #{OUT}"
else
  puts "\n#{errors.size} ERROR(S):"
  errors.each { |e| puts "  #{e}" }
  exit 1
end
